# Import necessary modules
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import call, patch

import pytest
from faker import Faker
from pandas._libs.tslibs.offsets import BDay, BusinessMonthEnd

from wbportfolio.models import Portfolio, RebalancingModel, TradeProposal
from wbportfolio.pms.typing import Portfolio as PortfolioDTO
from wbportfolio.pms.typing import Position

fake = Faker()


# Mark tests to use Django's database
@pytest.mark.django_db
class TestTradeProposal:
    # Test that the checked object is correctly set to the portfolio
    def test_checked_object(self, trade_proposal):
        """
        Verify that the checked object is the portfolio associated with the trade proposal.
        """
        assert trade_proposal.checked_object == trade_proposal.portfolio

    # Test that the evaluation date matches the trade date
    def test_check_evaluation_date(self, trade_proposal):
        """
        Ensure the evaluation date is the same as the trade date.
        """
        assert trade_proposal.check_evaluation_date == trade_proposal.trade_date

    # Test the validated trading service functionality
    def test_validated_trading_service(self, trade_proposal, asset_position_factory, trade_factory):
        """
        Validate that the effective and target portfolios are correctly calculated.
        """
        effective_date = (trade_proposal.trade_date - BDay(1)).date()

        # Create asset positions for testing
        a1 = asset_position_factory.create(
            portfolio=trade_proposal.portfolio, date=effective_date, weighting=Decimal("0.3")
        )
        a2 = asset_position_factory.create(
            portfolio=trade_proposal.portfolio, date=effective_date, weighting=Decimal("0.7")
        )

        # Create trades for testing
        t1 = trade_factory.create(
            trade_proposal=trade_proposal,
            weighting=Decimal("0.05"),
            portfolio=trade_proposal.portfolio,
            transaction_date=trade_proposal.trade_date,
            underlying_instrument=a1.underlying_quote,
        )
        t2 = trade_factory.create(
            trade_proposal=trade_proposal,
            weighting=Decimal("-0.05"),
            portfolio=trade_proposal.portfolio,
            transaction_date=trade_proposal.trade_date,
            underlying_instrument=a2.underlying_quote,
        )

        # Get the validated trading service
        validated_trading_service = trade_proposal.validated_trading_service

        # Assert effective and target portfolios are as expected
        assert validated_trading_service.effective_portfolio.to_dict() == {
            a1.underlying_quote.id: a1.weighting,
            a2.underlying_quote.id: a2.weighting,
        }
        assert validated_trading_service.target_portfolio.to_dict() == {
            a1.underlying_quote.id: a1.weighting + t1.weighting,
            a2.underlying_quote.id: a2.weighting + t2.weighting,
        }

    # Test the calculation of the last effective date
    def test_last_effective_date(self, trade_proposal, asset_position_factory):
        """
        Verify the last effective date is correctly determined based on asset positions.
        """
        # Without any positions, it should be the day before the trade date
        assert (
            trade_proposal.last_effective_date == (trade_proposal.trade_date - BDay(1)).date()
        ), "Last effective date without position should be t-1"

        # Create an asset position before the trade date
        a1 = asset_position_factory.create(
            portfolio=trade_proposal.portfolio, date=(trade_proposal.trade_date - BDay(5)).date()
        )
        a_noise = asset_position_factory.create(portfolio=trade_proposal.portfolio, date=trade_proposal.trade_date)  # noqa

        # The last effective date should still be the day before the trade date due to caching
        assert (
            trade_proposal.last_effective_date == (trade_proposal.trade_date - BDay(1)).date()
        ), "last effective date is cached, so it won't change as is"

        # Reset the cache property to recalculate
        del trade_proposal.last_effective_date

        # Now it should be the date of the latest position before the trade date
        assert (
            trade_proposal.last_effective_date == a1.date
        ), "last effective date is the latest position strictly lower than trade date"

    # Test finding the previous trade proposal
    def test_previous_trade_proposal(self, trade_proposal_factory):
        """
        Ensure the previous trade proposal is correctly identified as the last approved proposal before the current one.
        """
        tp = trade_proposal_factory.create()
        tp_previous_submit = trade_proposal_factory.create(  # noqa
            portfolio=tp.portfolio, status=TradeProposal.Status.SUBMIT, trade_date=(tp.trade_date - BDay(1)).date()
        )
        tp_previous_approve = trade_proposal_factory.create(
            portfolio=tp.portfolio, status=TradeProposal.Status.APPROVED, trade_date=(tp.trade_date - BDay(2)).date()
        )
        tp_next_approve = trade_proposal_factory.create(  # noqa
            portfolio=tp.portfolio, status=TradeProposal.Status.APPROVED, trade_date=(tp.trade_date + BDay(1)).date()
        )

        # The previous valid trade proposal should be the approved one strictly before the current proposal
        assert (
            tp.previous_trade_proposal == tp_previous_approve
        ), "the previous valid trade proposal is the strictly before and approved trade proposal"

    # Test finding the next trade proposal
    def test_next_trade_proposal(self, trade_proposal_factory):
        """
        Verify the next trade proposal is correctly identified as the first approved proposal after the current one.
        """
        tp = trade_proposal_factory.create()
        tp_next_submit = trade_proposal_factory.create(  # noqa
            portfolio=tp.portfolio, status=TradeProposal.Status.SUBMIT, trade_date=(tp.trade_date + BDay(1)).date()
        )
        tp_next_approve = trade_proposal_factory.create(
            portfolio=tp.portfolio, status=TradeProposal.Status.APPROVED, trade_date=(tp.trade_date + BDay(2)).date()
        )
        tp_previous_approve = trade_proposal_factory.create(  # noqa
            portfolio=tp.portfolio, status=TradeProposal.Status.APPROVED, trade_date=(tp.trade_date - BDay(1)).date()
        )

        # The next valid trade proposal should be the approved one strictly after the current proposal
        assert (
            tp.next_trade_proposal == tp_next_approve
        ), "the next valid trade proposal is the strictly after and approved trade proposal"

    # Test getting the default target portfolio
    def test__get_default_target_portfolio(self, trade_proposal, asset_position_factory):
        """
        Ensure the default target portfolio is set to the effective portfolio from the day before the trade date.
        """
        effective_date = (trade_proposal.trade_date - BDay(1)).date()

        # Create asset positions for testing
        a1 = asset_position_factory.create(
            portfolio=trade_proposal.portfolio, date=effective_date, weighting=Decimal("0.3")
        )
        a2 = asset_position_factory.create(
            portfolio=trade_proposal.portfolio, date=effective_date, weighting=Decimal("0.7")
        )
        asset_position_factory.create(portfolio=trade_proposal.portfolio, date=trade_proposal.trade_date)  # noise

        # The default target portfolio should match the effective portfolio
        assert trade_proposal._get_default_target_portfolio().to_dict() == {
            a1.underlying_quote.id: a1.weighting,
            a2.underlying_quote.id: a2.weighting,
        }

    # Test getting the default target portfolio with a rebalancing model
    @patch.object(RebalancingModel, "get_target_portfolio")
    def test__get_default_target_portfolio_with_rebalancer_model(self, mock_fct, trade_proposal, rebalancer_factory):
        """
        Verify that the target portfolio is correctly obtained from a rebalancing model.
        """
        # Expected target portfolio from the rebalancing model
        expected_target_portfolio = PortfolioDTO(
            positions=(Position(underlying_instrument=1, weighting=Decimal(1), date=trade_proposal.trade_date),)
        )
        mock_fct.return_value = expected_target_portfolio

        # Create a rebalancer for testing
        rebalancer = rebalancer_factory.create(
            portfolio=trade_proposal.portfolio, parameters={"rebalancer_parameter": "A"}
        )
        trade_proposal.rebalancing_model = rebalancer.rebalancing_model
        trade_proposal.save()

        # Additional keyword arguments for the rebalancing model
        extra_kwargs = {"test": "test"}

        # Combine rebalancer parameters with extra keyword arguments
        expected_kwargs = rebalancer.parameters
        expected_kwargs.update(extra_kwargs)

        # Assert the target portfolio matches the expected output from the rebalancing model
        assert (
            trade_proposal._get_default_target_portfolio(**extra_kwargs) == expected_target_portfolio
        ), "We expect the target portfolio to be whatever is returned by the rebalancer model"
        mock_fct.assert_called_once_with(
            trade_proposal.portfolio, trade_proposal.trade_date, trade_proposal.last_effective_date, **expected_kwargs
        )

    # Test normalizing trades
    def test_normalize_trades(self, trade_proposal, trade_factory):
        """
        Ensure trades are normalized to sum up to 1, handling quantization errors.
        """
        # Create trades for testing
        t1 = trade_factory.create(
            trade_proposal=trade_proposal,
            transaction_date=trade_proposal.trade_date,
            portfolio=trade_proposal.portfolio,
            weighting=Decimal(0.2),
        )
        t2 = trade_factory.create(
            trade_proposal=trade_proposal,
            transaction_date=trade_proposal.trade_date,
            portfolio=trade_proposal.portfolio,
            weighting=Decimal(0.26),
        )
        t3 = trade_factory.create(
            trade_proposal=trade_proposal,
            transaction_date=trade_proposal.trade_date,
            portfolio=trade_proposal.portfolio,
            weighting=Decimal(0.14),
        )

        # Normalize trades
        trade_proposal.normalize_trades()

        # Refresh trades from the database
        t1.refresh_from_db()
        t2.refresh_from_db()
        t3.refresh_from_db()

        # Expected normalized weights
        normalized_t1_weight = Decimal("0.333333")
        normalized_t2_weight = Decimal("0.433333")
        normalized_t3_weight = Decimal("0.233333")

        # Calculate quantization error
        quantize_error = Decimal(1) - (normalized_t1_weight + normalized_t2_weight + normalized_t3_weight)

        # Assert quantization error exists and weights are normalized correctly
        assert quantize_error
        assert t1.weighting == normalized_t1_weight
        assert t2.weighting == normalized_t2_weight + quantize_error  # Add quantize error to the largest position
        assert t3.weighting == normalized_t3_weight

    # Test resetting trades
    def test_reset_trades(self, trade_proposal, instrument_factory, asset_position_factory):
        """
        Verify trades are correctly reset based on effective and target portfolios.
        """
        effective_date = trade_proposal.last_effective_date

        # Create instruments for testing
        i1 = instrument_factory.create(currency=trade_proposal.portfolio.currency)
        i2 = instrument_factory.create(currency=trade_proposal.portfolio.currency)
        i3 = instrument_factory.create(currency=trade_proposal.portfolio.currency)

        # Build initial effective portfolio constituting only from two positions of i1 and i2
        asset_position_factory.create(
            portfolio=trade_proposal.portfolio, date=effective_date, underlying_instrument=i1, weighting=Decimal("0.7")
        )
        asset_position_factory.create(
            portfolio=trade_proposal.portfolio, date=effective_date, underlying_instrument=i2, weighting=Decimal("0.3")
        )

        # build the target portfolio
        target_portfolio = PortfolioDTO(
            positions=(
                Position(underlying_instrument=i2.id, date=trade_proposal.trade_date, weighting=Decimal("0.4")),
                Position(underlying_instrument=i3.id, date=trade_proposal.trade_date, weighting=Decimal("0.6")),
            )
        )

        # Reset trades
        trade_proposal.reset_trades(target_portfolio=target_portfolio)

        # Get trades for each instrument
        t1 = trade_proposal.trades.get(underlying_instrument=i1)
        t2 = trade_proposal.trades.get(underlying_instrument=i2)
        t3 = trade_proposal.trades.get(underlying_instrument=i3)

        # Assert trade weights are correctly reset
        assert t1.weighting == Decimal("-0.7")
        assert t2.weighting == Decimal("0.1")
        assert t3.weighting == Decimal("0.6")

        # build the target portfolio
        new_target_portfolio = PortfolioDTO(
            positions=(
                Position(underlying_instrument=i1.id, date=trade_proposal.trade_date, weighting=Decimal("0.2")),
                Position(underlying_instrument=i2.id, date=trade_proposal.trade_date, weighting=Decimal("0.3")),
                Position(underlying_instrument=i3.id, date=trade_proposal.trade_date, weighting=Decimal("0.5")),
            )
        )

        trade_proposal.reset_trades(target_portfolio=new_target_portfolio)
        # Refetch the trades for each instrument
        t1.refresh_from_db()
        t2.refresh_from_db()
        t3.refresh_from_db()
        # Assert existing trade weights are correctly updated
        assert t1.weighting == Decimal("-0.5")
        assert t2.weighting == Decimal("0")
        assert t3.weighting == Decimal("0.5")

    # Test replaying trade proposals
    @patch.object(Portfolio, "drift_weights")
    def test_replay(self, mock_fct, trade_proposal_factory):
        """
        Ensure replaying trade proposals correctly calls drift_weights for each period.
        """
        mock_fct.return_value = None, None

        # Create approved trade proposals for testing
        tp0 = trade_proposal_factory.create(status=TradeProposal.Status.APPROVED)
        tp1 = trade_proposal_factory.create(
            portfolio=tp0.portfolio,
            status=TradeProposal.Status.APPROVED,
            trade_date=(tp0.trade_date + BusinessMonthEnd(1)).date(),
        )
        tp2 = trade_proposal_factory.create(
            portfolio=tp0.portfolio,
            status=TradeProposal.Status.APPROVED,
            trade_date=(tp1.trade_date + BusinessMonthEnd(1)).date(),
        )

        # Replay trade proposals
        tp0.replay()

        # Expected calls to drift_weights
        expected_calls = [
            call(tp0.trade_date, tp1.trade_date - timedelta(days=1)),
            call(tp1.trade_date, tp2.trade_date - timedelta(days=1)),
            call(tp2.trade_date, date.today()),
        ]

        # Assert drift_weights was called as expected
        mock_fct.assert_has_calls(expected_calls)

        # Test stopping replay on a non-approved proposal
        tp1.status = TradeProposal.Status.FAILED
        tp1.save()
        expected_calls = [call(tp0.trade_date, tp1.trade_date - timedelta(days=1))]
        mock_fct.assert_has_calls(expected_calls)

    # Test estimating shares for a trade
    @patch.object(Portfolio, "get_total_asset_value")
    def test_get_estimated_shares(
        self, mock_fct, trade_proposal, trade_factory, instrument_price_factory, instrument_factory
    ):
        """
        Verify shares estimation based on trade weighting and instrument price.
        """
        portfolio = trade_proposal.portfolio
        instrument = instrument_factory.create(currency=portfolio.currency)
        trade = trade_factory.create(
            trade_proposal=trade_proposal,
            transaction_date=trade_proposal.trade_date,
            portfolio=portfolio,
            underlying_instrument=instrument,
        )
        trade.refresh_from_db()
        underlying_quote_price = instrument_price_factory.create(instrument=instrument, date=trade.transaction_date)
        mock_fct.return_value = Decimal(1_000_000)  # 1 million cash

        # Assert estimated shares are correctly calculated
        assert (
            trade_proposal.get_estimated_shares(trade.weighting, trade.underlying_instrument)
            == Decimal(1_000_000) * trade.weighting / underlying_quote_price.net_value
        )

    @patch.object(Portfolio, "get_total_asset_value")
    def test_get_estimated_target_cash(self, mock_fct, trade_proposal, trade_factory, cash_factory):
        mock_fct.return_value = Decimal(1_000_000)  # 1 million cash
        cash = cash_factory.create(currency=trade_proposal.portfolio.currency)
        trade_factory.create(  # equity trade
            trade_proposal=trade_proposal,
            transaction_date=trade_proposal.trade_date,
            portfolio=trade_proposal.portfolio,
            weighting=Decimal("0.7"),
        )
        trade_factory.create(  # cash trade
            trade_proposal=trade_proposal,
            transaction_date=trade_proposal.trade_date,
            portfolio=trade_proposal.portfolio,
            underlying_instrument=cash,
            weighting=Decimal("0.2"),
        )

        target_cash_position = trade_proposal.get_estimated_target_cash(trade_proposal.portfolio.currency)
        assert target_cash_position.weighting == Decimal("0.2") + Decimal("1.0") - (Decimal("0.7") + Decimal("0.2"))
        assert target_cash_position.initial_shares == Decimal(1_000_000) * Decimal("0.3")

    def test_trade_proposal_update_inception_date(self, trade_proposal_factory, portfolio, instrument_factory):
        # Check that if we create a prior trade proposal, the instrument inception date is updated accordingly
        instrument = instrument_factory.create(inception_date=None)
        instrument.portfolios.add(portfolio)
        tp = trade_proposal_factory.create(portfolio=portfolio)
        instrument.refresh_from_db()
        assert instrument.inception_date == (tp.trade_date + BDay(1)).date()

        tp2 = trade_proposal_factory.create(portfolio=portfolio, trade_date=tp.trade_date - BDay(1))
        instrument.refresh_from_db()
        assert instrument.inception_date == (tp2.trade_date + BDay(1)).date()
