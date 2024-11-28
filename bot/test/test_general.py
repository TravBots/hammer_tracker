import pytest
import discord
from unittest.mock import AsyncMock, MagicMock
from bot.commands.scout import scout
from bot.commands.cfd import cfd
from utils.constants import Colors, crop_production
from interactions.cfd import Cfd


class TestCommands:
    @pytest.fixture
    def mock_interaction(self):
        interaction = MagicMock(spec=discord.Interaction)
        interaction.response = AsyncMock()
        return interaction

    @pytest.mark.asyncio
    async def test_scout_calculation(self, mock_interaction):
        # Test case inputs
        crop_1 = 1000
        crop_2 = 800
        seconds_between_scoutings = 3600
        field_levels = 10
        oasis_bonus = 0.25
        reins_in_village = 100
        population = 50
        cropper_type = 9
        flour_mill_bakery = 0.50
        gold_bonus = 0.25

        # Calculate expected result
        base_production = crop_production[field_levels] * cropper_type
        with_oases_mill_bakery = (
            (base_production * oasis_bonus)
            + (base_production * flour_mill_bakery)
            + base_production
        )
        with_gold_bonus = with_oases_mill_bakery * (1 + gold_bonus)
        expected_hammer = (
            (((crop_1 - crop_2) / seconds_between_scoutings) * 3600)
            - reins_in_village
            + with_gold_bonus
            - population
        )

        # Call the scout command's callback
        await scout.callback(
            mock_interaction,
            crop_1,
            crop_2,
            seconds_between_scoutings,
            field_levels,
            oasis_bonus,
            reins_in_village,
            population,
            cropper_type,
            flour_mill_bakery,
            gold_bonus,
        )

        # Verify the response
        mock_interaction.response.send_message.assert_called_once()
        call_args = mock_interaction.response.send_message.call_args
        embed = call_args[1]["embed"]

        assert embed.color.value == Colors.SUCCESS
        assert len(embed.fields) == 1
        assert embed.fields[0].name == "Crop Scout Result"
        assert f"{int(expected_hammer):,}" in embed.fields[0].value

    @pytest.mark.asyncio
    async def test_scout_edge_cases_min(self, mock_interaction):
        # Test with minimum field levels
        crop_1 = 1000
        crop_2 = 900
        seconds_between_scoutings = 3600
        field_levels = 10
        oasis_bonus = 0.0
        reins_in_village = 0
        population = 0
        cropper_type = 6
        flour_mill_bakery = 0.05
        gold_bonus = 0.0

        await scout.callback(
            mock_interaction,
            crop_1,
            crop_2,
            seconds_between_scoutings,
            field_levels,
            oasis_bonus,
            reins_in_village,
            population,
            cropper_type,
            flour_mill_bakery,
            gold_bonus,
        )
        mock_interaction.response.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_scout_edge_cases_max(self, mock_interaction):
        # Test with maximum field levels
        crop_1 = 10000
        crop_2 = 9000
        seconds_between_scoutings = 3600
        field_levels = 20
        oasis_bonus = 1.50
        reins_in_village = 1000
        population = 1000
        cropper_type = 15
        flour_mill_bakery = 0.50
        gold_bonus = 0.25

        await scout.callback(
            mock_interaction,
            crop_1,
            crop_2,
            seconds_between_scoutings,
            field_levels,
            oasis_bonus,
            reins_in_village,
            population,
            cropper_type,
            flour_mill_bakery,
            gold_bonus,
        )
        mock_interaction.response.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_cfd_modal(self, mock_interaction):
        # Test that the CFD command opens the modal
        await cfd.callback(mock_interaction)

        # Verify the modal was sent
        mock_interaction.response.send_modal.assert_called_once()

        # Get the modal and verify its type
        modal = mock_interaction.response.send_modal.call_args[0][0]
        assert issubclass(type(modal), Cfd) or isinstance(modal, Cfd)
        assert modal.title == "CFD"

        # Verify the modal has all required fields
        expected_fields = [
            "cfd_title",
            "coordinates",
            "land_time",
            "amount_requested",
            "notes",
        ]

        for field in expected_fields:
            assert hasattr(modal, field)
