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
            personal_entry = False
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
    ) -> str:
        """Calculate raiding rates and create ASCII table response"""
        logger.info("Calculating raid rates")
        now = datetime.utcnow()

        # Get the most recent Sunday at 00:30 UTC
        days_since_sunday = now.weekday() + 1
        last_sunday = now - timedelta(days=days_since_sunday % 7)
        week_start = last_sunday.replace(hour=0, minute=30, second=0, microsecond=0)

        # If we're before Sunday 00:30, use previous week's Sunday
        if now < week_start:
            week_start = week_start - timedelta(days=7)
        logger.debug(f"Using week start time: {week_start}")

        # Individual box width (3 boxes per row)
        BOX_WIDTH = 30
        TOTAL_WIDTH = BOX_WIDTH * 3

        def create_player_box(
            rank: int, name: str, value1: str, value2: str
        ) -> List[str]:
            """Helper function to create a single player box"""
            border = "*" * BOX_WIDTH
            title_row = f"*{f'{rank}. {name}'.center(BOX_WIDTH-2)}*"
            half_width = (BOX_WIDTH - 3) // 2
            value_row = (
                f"*{value1.center(half_width)}*{value2.center(BOX_WIDTH-half_width-3)}*"
            )
            return [border, title_row, border, value_row, border]

        # Process entries in groups of 3
        all_boxes = []
        current_row = []

        def process_entry(rank: int, name: str, current_total: int) -> List[str]:
            """Process a single entry and return its box lines"""
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
                return create_player_box(rank, name, "New", f"{current_total:,}")

            # Calculate rates
            end_total, end_time = recent_records[0]
            start_total, start_time = recent_records[1]
            end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            hours_elapsed = (end_time - start_time).total_seconds() / 3600
            current_rate = (
                f"{int((end_total - start_total) / hours_elapsed/1000)}k"
                if hours_elapsed > 0
                else "N/A"
            )

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
                        f"{int((current_total - start_total) / hours_elapsed/1000)}k"
                    )

            return create_player_box(
                rank, name, f"C:{current_rate}/h", f"W:{week_rate}/h"
            )

        # Process top entries
        rows = []
        current_row = []
        for entry in top_entries:
            current_row.append(process_entry(*entry))
            if len(current_row) == 3:
                # Combine the boxes into a row
                row_lines = []
                for i in range(5):  # 5 lines per box
                    row_lines.append("".join(box[i] for box in current_row))
                rows.extend(row_lines)
                current_row = []

        # Handle any remaining entries in the last row
        if current_row:
            # Pad with empty boxes if needed
            while len(current_row) < 3:
                current_row.append([" " * BOX_WIDTH] * 5)
            row_lines = []
            for i in range(5):
                row_lines.append("".join(box[i] for box in current_row))
            rows.extend(row_lines)

        # Add personal entry as a separate row if it exists
        if personal_entry:
            rows.extend(process_entry(*personal_entry))

        return "```\n" + "\n".join(rows) + "\n```"
