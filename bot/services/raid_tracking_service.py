import re
import sqlite3
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from utils.logger import logger
from utils.constants import Colors
import discord


class RaidTrackingService:
    def __init__(self):
        # Match both "123." and "123" formats for rank
        self.leaderboard_pattern = re.compile(
            r"(\d+)\.?\s+([^\d]+?)\s+[\u202d\u202c\u200f\u200e]*([0-9,]+)"
        )

    def _parse_leaderboard(self, content: str) -> List[Tuple[int, str, int]]:
        """Parse leaderboard text into (rank, name, total) tuples"""
        logger.debug("Parsing leaderboard content")
        matches = self.leaderboard_pattern.finditer(content)
        results = []

        for match in matches:
            rank = int(match.group(1))
            name = match.group(2).strip()
            total = int(match.group(3).replace(",", ""))
            results.append((rank, name, total))

        logger.debug(f"Parsed {len(results)} entries from leaderboard")

        # Validate we got all entries (10 top + 1 personal)
        if len(results) != 11:
            logger.warning(f"Expected 11 entries but got {len(results)}")

        return results

    def _round_to_last_update(self, dt: datetime) -> datetime:
        """Round timestamp to the most recent raid board update time (XX:30)"""
        # Always round to the previous :30 mark
        result = None
        if dt.minute >= 30:
            result = dt.replace(minute=30, second=0, microsecond=0)
        else:
            # If we're before :30, use previous hour's :30
            result = dt.replace(minute=30, second=0, microsecond=0) - timedelta(hours=1)

        logger.debug(f"Rounded {dt} to {result}")
        return result

    async def process_leaderboard(
        self, message: discord.Message, db_path: str
    ) -> discord.Embed:
        """Process a leaderboard message and return stats embed"""
        try:
            logger.info(f"Processing leaderboard from channel {message.channel.id}")
            entries = self._parse_leaderboard(message.content)
            if not entries:
                logger.warning("No entries found in leaderboard message")
                return None

            now = datetime.utcnow()
            logger.debug(f"Current time: {now}")

            # Split into top 10 and personal entry
            top_entries = [e for e in entries if e[0] <= 10]
            personal_entry = next((e for e in entries if e[0] > 10), None)
            logger.info(
                f"Found {len(top_entries)} top entries and {'a' if personal_entry else 'no'} personal entry"
            )

            # Store entries
            with sqlite3.connect(db_path) as conn:
                # Store top 10 with rounded timestamp
                rounded_time = self._round_to_last_update(now)
                for rank, name, total in top_entries:
                    # Check if record already exists
                    existing = conn.execute(
                        """
                        SELECT id FROM RAID_TRACKING 
                        WHERE player_name = ? 
                        AND recorded_at = ?
                        AND is_personal = FALSE
                        """,
                        (name, rounded_time),
                    ).fetchone()

                    if existing:
                        logger.debug(
                            f"Skipping duplicate entry for {name} at {rounded_time}"
                        )
                        continue

                    logger.debug(
                        f"Storing top entry: {name} (rank {rank}) with {total:,} at {rounded_time}"
                    )
                    conn.execute(
                        """
                        INSERT INTO RAID_TRACKING (
                            player_name, rank, total_raided, channel_id, recorded_at, is_personal
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            name,
                            rank,
                            total,
                            str(message.channel.id),
                            rounded_time,
                            False,
                        ),
                    )

                # Store personal entry with exact timestamp
                if personal_entry:
                    rank, name, total = personal_entry
                    # Check if record already exists
                    existing = conn.execute(
                        """
                        SELECT id FROM RAID_TRACKING 
                        WHERE player_name = ? 
                        AND recorded_at = ?
                        AND is_personal = TRUE
                        """,
                        (name, now),
                    ).fetchone()

                    if not existing:
                        logger.debug(
                            f"Storing personal entry: {name} (rank {rank}) with {total:,}"
                        )
                        conn.execute(
                            """
                            INSERT INTO RAID_TRACKING (
                                player_name, rank, total_raided, channel_id, recorded_at, is_personal
                            ) VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            (name, rank, total, str(message.channel.id), now, True),
                        )
                    else:
                        logger.debug(
                            f"Skipping duplicate personal entry for {name} at {now}"
                        )

            # Calculate raid rates
            return await self._calculate_raid_rates(conn, top_entries, personal_entry)

        except Exception as e:
            logger.error(f"Error processing leaderboard: {e}", exc_info=True)
            return None

    async def _calculate_raid_rates(
        self,
        conn: sqlite3.Connection,
        top_entries: List[Tuple[int, str, int]],
        personal_entry: Optional[Tuple[int, str, int]],
    ) -> discord.Embed:
        """Calculate raiding rates and create response embed"""
        logger.info("Calculating raid rates")
        embed = discord.Embed(title="Raiding Rates", color=Colors.SUCCESS)
        now = datetime.utcnow()

        # Get the most recent Sunday at 00:30 UTC
        days_since_sunday = now.weekday() + 1
        last_sunday = now - timedelta(days=days_since_sunday % 7)
        week_start = last_sunday.replace(hour=0, minute=30, second=0, microsecond=0)

        # If we're before Sunday 00:30, use previous week's Sunday
        if now < week_start:
            week_start = week_start - timedelta(days=7)
        logger.debug(f"Using week start time: {week_start}")

        # Calculate for top 10
        top_rates = []
        for rank, name, current_total in top_entries:
            logger.debug(f"Calculating rates for {name} (rank {rank})")

            # Get two most recent records for current rate, but only within this week
            recent_records = conn.execute(
                """
                SELECT total_raided, recorded_at
                FROM RAID_TRACKING 
                WHERE player_name = ? 
                AND is_personal = FALSE
                AND recorded_at >= ?
                ORDER BY recorded_at DESC
                LIMIT 2
                """,
                (name, week_start),
            ).fetchall()

            if len(recent_records) < 2:
                # New player with insufficient history this week
                top_rates.append(
                    f"{rank}. {name}:\n⭐ New to leaderboard! ⭐\nTotal: {current_total:,}"
                )
                continue

            end_total, end_time = recent_records[0]  # Most recent record
            start_total, start_time = recent_records[1]  # Second most recent
            end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            hours_elapsed = (end_time - start_time).total_seconds() / 3600
            current_rate = 0
            if hours_elapsed > 0:
                current_rate = f"{int((end_total - start_total) / hours_elapsed):,}"

            # Get weekly average
            week_start_record = conn.execute(
                """
                SELECT total_raided, recorded_at
                FROM RAID_TRACKING 
                WHERE player_name = ? 
                AND recorded_at >= ?
                AND is_personal = FALSE
                ORDER BY recorded_at ASC
                LIMIT 1
                """,
                (name, week_start),
            ).fetchone()

            week_rate = "N/A"
            if week_start_record:
                start_total = week_start_record[0]
                start_time = datetime.strptime(
                    week_start_record[1], "%Y-%m-%d %H:%M:%S"
                )
                hours_elapsed = (now - start_time).total_seconds() / 3600
                if hours_elapsed > 0:
                    week_rate = (
                        f"{int((current_total - start_total) / hours_elapsed):,}"
                    )
                    logger.debug(
                        f"Calculated week rate for {name}: {week_rate}/hr over {hours_elapsed:.1f} hours"
                    )
                    logger.debug(
                        f"*******: current_total: {current_total}, start_total: {start_total}, hours_elapsed: {hours_elapsed}"
                    )

            top_rates.append(
                f"{rank}. {name}:\nCurrent: {current_rate}/hr\nWeek Avg: {week_rate}/hr"
            )

        if top_rates:
            embed.add_field(
                name="Top Raiders",
                value="\n".join(top_rates),
                inline=False,
            )

        # Handle personal entry
        if personal_entry:
            rank, name, current_total = personal_entry
            logger.debug(f"Calculating personal rates for {name}")

            recent_records = conn.execute(
                """
                SELECT total_raided, recorded_at
                FROM RAID_TRACKING 
                WHERE player_name = ? 
                AND is_personal = TRUE
                AND recorded_at >= ?
                ORDER BY recorded_at DESC
                LIMIT 2
                """,
                (name, week_start),
            ).fetchall()

            if len(recent_records) < 2:
                embed.add_field(
                    name=f"Your Raiding Stats ({name})",
                    value=f"⭐ Welcome to the leaderboard! ⭐\nTotal: {current_total:,}",
                    inline=False,
                )
            else:
                end_total, end_time = recent_records[0]  # Most recent record
                start_total, start_time = recent_records[1]  # Second most recent
                end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                hours_elapsed = (end_time - start_time).total_seconds() / 3600
                if hours_elapsed > 0:
                    current_rate = f"{int((end_total - start_total) / hours_elapsed):,}"

                # Get weekly average
                week_start_record = conn.execute(
                    """
                    SELECT total_raided, recorded_at
                    FROM RAID_TRACKING 
                    WHERE player_name = ? 
                    AND recorded_at >= ?
                    AND is_personal = TRUE
                    ORDER BY recorded_at ASC
                    LIMIT 1
                    """,
                    (name, week_start),
                ).fetchone()

                week_rate = "N/A"
                if week_start_record:
                    start_total = week_start_record[0]
                    start_time = datetime.strptime(
                        week_start_record[1], "%Y-%m-%d %H:%M:%S"
                    )
                    hours_elapsed = (now - start_time).total_seconds() / 3600
                    if hours_elapsed > 0:
                        week_rate = (
                            f"{int((current_total - start_total) / hours_elapsed):,}"
                        )

                embed.add_field(
                    name=f"Your Raiding Rate ({name})",
                    value=f"Current: {current_rate}/hr\nWeek Average: {week_rate}/hr",
                    inline=False,
                )

        return embed
