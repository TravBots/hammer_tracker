import re
import sqlite3
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from utils.logger import logger
from utils.constants import Colors
import discord


class RaidTrackingService:
    def __init__(self):
        self.leaderboard_pattern = re.compile(
            r"(\d+)\.\s+([^\d]+?)\s+[\u202d\u202c\u200f\u200e]*([0-9,]+)"
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
        embed = discord.Embed(title="Raiding Rates (per hour)", color=Colors.SUCCESS)
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
            logger.debug(f"Calculating rate for {name} (rank {rank})")
            # Get the earliest record after the weekly reset
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

            if week_start_record:
                start_total = week_start_record[0]
                start_time = datetime.strptime(
                    week_start_record[1], "%Y-%m-%d %H:%M:%S"
                )
                logger.debug(
                    f"Found start record for {name}: {start_total:,} at {start_time}"
                )

                hours_elapsed = (now - start_time).total_seconds() / 3600
                if hours_elapsed > 0:
                    hourly_rate = int((current_total - start_total) / hours_elapsed)
                    logger.debug(
                        f"Calculated rate for {name}: {hourly_rate:,}/hr over {hours_elapsed:.1f} hours"
                    )
                    top_rates.append(f"{rank}. {name}: {hourly_rate:,}/hr")
            else:
                logger.debug(f"No week start record found for {name}")

        if top_rates:
            embed.add_field(
                name="Top Raiders (Week Average)",
                value="\n".join(top_rates),
                inline=False,
            )

        # Calculate personal rate if available
        if personal_entry:
            rank, name, current_total = personal_entry
            logger.debug(f"Calculating personal rate for {name}")

            two_hours_ago = self._round_to_last_update(now - timedelta(hours=2))
            logger.debug(f"Looking for records between {two_hours_ago} and {now}")

            prev_records = conn.execute(
                """
                SELECT total_raided, recorded_at
                FROM RAID_TRACKING 
                WHERE player_name = ? 
                AND recorded_at >= ?
                AND recorded_at < ?
                AND is_personal = TRUE
                ORDER BY recorded_at DESC
            """,
                (name, two_hours_ago, now),
            ).fetchall()

            if prev_records:
                logger.debug(f"Found {len(prev_records)} previous records for {name}")
                oldest_record = prev_records[-1]
                start_total = oldest_record[0]
                start_time = datetime.strptime(oldest_record[1], "%Y-%m-%d %H:%M:%S")
                logger.debug(f"Using oldest record: {start_total:,} at {start_time}")

                hours_elapsed = (now - start_time).total_seconds() / 3600
                if hours_elapsed > 0:
                    recent_rate = int((current_total - start_total) / hours_elapsed)
                    logger.debug(
                        f"Calculated recent rate for {name}: {recent_rate:,}/hr over {hours_elapsed:.1f} hours"
                    )

                    # Also get weekly average
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

                    if week_start_record:
                        start_total = week_start_record[0]
                        start_time = datetime.strptime(
                            week_start_record[1], "%Y-%m-%d %H:%M:%S"
                        )
                        logger.debug(
                            f"Found week start record for {name}: {start_total:,} at {start_time}"
                        )

                        hours_elapsed = (now - start_time).total_seconds() / 3600
                        if hours_elapsed > 0:
                            week_rate = int(
                                (current_total - start_total) / hours_elapsed
                            )
                            logger.debug(
                                f"Calculated week rate for {name}: {week_rate:,}/hr over {hours_elapsed:.1f} hours"
                            )
                            embed.add_field(
                                name=f"Your Raiding Rate ({name})",
                                value=f"Recent: {recent_rate:,}/hr\nWeek Average: {week_rate:,}/hr",
                                inline=False,
                            )
                    else:
                        logger.debug(f"No week start record found for {name}")
                        embed.add_field(
                            name=f"Your Raiding Rate ({name})",
                            value=f"Recent: {recent_rate:,}/hr",
                            inline=False,
                        )
            else:
                logger.debug(f"No recent records found for {name}")

        return embed
