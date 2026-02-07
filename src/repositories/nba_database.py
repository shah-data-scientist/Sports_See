"""
FILE: nba_database.py
STATUS: Active
RESPONSIBILITY: SQLAlchemy models and repository for NBA statistics database
LAST MAJOR UPDATE: 2026-02-07
MAINTAINER: Shahu
"""

import logging
from pathlib import Path
from typing import Any

from sqlalchemy import (
    DECIMAL,
    Column,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    relationship,
    sessionmaker,
)

from src.core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class TeamModel(Base):
    """Team table - stores NBA team information."""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    abbreviation = Column(String(5), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)

    # Relationships
    players = relationship("PlayerModel", back_populates="team_rel", cascade="all, delete-orphan")
    stats = relationship("PlayerStatsModel", back_populates="team_rel", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Team(abbreviation='{self.abbreviation}', name='{self.name}')>"


class PlayerModel(Base):
    """Player table - stores NBA player basic information."""

    __tablename__ = "players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    team_abbr = Column(String(5), ForeignKey("teams.abbreviation"), nullable=False)
    age = Column(Integer, nullable=False)

    # Relationships
    team_rel = relationship("TeamModel", back_populates="players")
    stats = relationship("PlayerStatsModel", back_populates="player_rel", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Player(name='{self.name}', team='{self.team_abbr}', age={self.age})>"


class PlayerStatsModel(Base):
    """Player statistics table - stores complete NBA player season statistics."""

    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    team_abbr = Column(String(5), ForeignKey("teams.abbreviation"), nullable=False, index=True)

    # Games
    gp = Column(Integer, nullable=False, comment="Games played")
    w = Column(Integer, nullable=False, comment="Wins")
    l = Column(Integer, nullable=False, comment="Losses")
    min = Column(DECIMAL(5, 1), nullable=False, comment="Minutes per game")

    # Scoring
    pts = Column(Integer, nullable=False, comment="Total points")
    fgm = Column(Integer, nullable=False, comment="Field goals made")
    fga = Column(Integer, nullable=False, comment="Field goals attempted")
    fg_pct = Column(DECIMAL(5, 1), nullable=True, comment="Field goal percentage")

    # Three-pointers
    three_pm = Column(Integer, nullable=False, comment="3-point shots made")
    three_pa = Column(Integer, nullable=False, comment="3-point shots attempted")
    three_pct = Column(DECIMAL(5, 1), nullable=True, comment="3-point percentage")

    # Free throws
    ftm = Column(Integer, nullable=False, comment="Free throws made")
    fta = Column(Integer, nullable=False, comment="Free throws attempted")
    ft_pct = Column(DECIMAL(5, 1), nullable=True, comment="Free throw percentage")

    # Rebounds
    oreb = Column(Integer, nullable=False, comment="Offensive rebounds")
    dreb = Column(Integer, nullable=False, comment="Defensive rebounds")
    reb = Column(Integer, nullable=False, comment="Total rebounds")

    # Other stats
    ast = Column(Integer, nullable=False, comment="Assists")
    tov = Column(Integer, nullable=False, comment="Turnovers")
    stl = Column(Integer, nullable=False, comment="Steals")
    blk = Column(Integer, nullable=False, comment="Blocks")
    pf = Column(Integer, nullable=False, comment="Personal fouls")

    # Performance
    fp = Column(DECIMAL(7, 2), nullable=False, comment="Fantasy points")
    dd2 = Column(Integer, nullable=False, comment="Double-doubles")
    td3 = Column(Integer, nullable=False, comment="Triple-doubles")
    plus_minus = Column(DECIMAL(6, 1), nullable=False, comment="Plus/minus")

    # Advanced metrics
    off_rtg = Column(DECIMAL(6, 1), nullable=False, comment="Offensive rating")
    def_rtg = Column(DECIMAL(6, 1), nullable=False, comment="Defensive rating")
    net_rtg = Column(DECIMAL(6, 1), nullable=False, comment="Net rating")

    ast_pct = Column(DECIMAL(5, 1), nullable=False, comment="Assist percentage")
    ast_to = Column(DECIMAL(5, 2), nullable=False, comment="Assist/turnover ratio")
    ast_ratio = Column(DECIMAL(5, 1), nullable=False, comment="Assist ratio")

    oreb_pct = Column(DECIMAL(5, 1), nullable=False, comment="Offensive rebound %")
    dreb_pct = Column(DECIMAL(5, 1), nullable=False, comment="Defensive rebound %")
    reb_pct = Column(DECIMAL(5, 1), nullable=False, comment="Total rebound %")

    to_ratio = Column(DECIMAL(5, 1), nullable=False, comment="Turnover ratio")
    efg_pct = Column(DECIMAL(5, 1), nullable=False, comment="Effective FG %")
    ts_pct = Column(DECIMAL(5, 1), nullable=False, comment="True shooting %")
    usg_pct = Column(DECIMAL(5, 1), nullable=False, comment="Usage %")

    pace = Column(DECIMAL(5, 1), nullable=False, comment="Pace")
    pie = Column(DECIMAL(5, 3), nullable=False, comment="Player impact estimate")
    poss = Column(Integer, nullable=False, comment="Possessions")

    # Relationships
    player_rel = relationship("PlayerModel", back_populates="stats")
    team_rel = relationship("TeamModel", back_populates="stats")

    def __repr__(self) -> str:
        """String representation."""
        return f"<PlayerStats(player_id={self.player_id}, pts={self.pts}, gp={self.gp})>"


class NBADatabase:
    """Repository for NBA statistics database operations."""

    def __init__(self, db_path: str | None = None):
        """Initialize NBA database.

        Args:
            db_path: Path to SQLite database file (default: database/nba_stats.db)
        """
        if db_path is None:
            db_path = str(Path(settings.database_dir) / "nba_stats.db")

        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Create engine
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

        logger.info(f"NBA database initialized: {db_path}")

    def create_tables(self) -> None:
        """Create all database tables."""
        Base.metadata.create_all(self.engine)
        logger.info("NBA database tables created")

    def drop_tables(self) -> None:
        """Drop all database tables."""
        Base.metadata.drop_all(self.engine)
        logger.info("NBA database tables dropped")

    def get_session(self) -> Session:
        """Get a new database session.

        Returns:
            SQLAlchemy Session instance

        Example:
            with db.get_session() as session:
                teams = session.query(TeamModel).all()
        """
        return self.SessionLocal()

    def close(self) -> None:
        """Close database connections."""
        self.engine.dispose()
        logger.info("NBA database connections closed")

    def add_team(self, session: Session, abbreviation: str, name: str) -> TeamModel:
        """Add a team to the database.

        Args:
            session: Database session
            abbreviation: Team abbreviation (e.g., 'LAL')
            name: Full team name (e.g., 'Los Angeles Lakers')

        Returns:
            Created TeamModel instance
        """
        team = TeamModel(abbreviation=abbreviation, name=name)
        session.add(team)
        return team

    def add_player(self, session: Session, name: str, team_abbr: str, age: int) -> PlayerModel:
        """Add a player to the database.

        Args:
            session: Database session
            name: Player name
            team_abbr: Team abbreviation
            age: Player age

        Returns:
            Created PlayerModel instance
        """
        player = PlayerModel(name=name, team_abbr=team_abbr, age=age)
        session.add(player)
        return player

    def add_player_stats(self, session: Session, player_id: int, stats: dict[str, Any]) -> PlayerStatsModel:
        """Add player statistics to the database.

        Args:
            session: Database session
            player_id: Player ID
            stats: Dictionary of statistics

        Returns:
            Created PlayerStatsModel instance
        """
        stats_model = PlayerStatsModel(player_id=player_id, **stats)
        session.add(stats_model)
        return stats_model

    def get_player_by_name(self, session: Session, name: str) -> PlayerModel | None:
        """Get player by name.

        Args:
            session: Database session
            name: Player name

        Returns:
            PlayerModel instance or None if not found
        """
        return session.query(PlayerModel).filter(PlayerModel.name == name).first()

    def get_team_by_abbreviation(self, session: Session, abbreviation: str) -> TeamModel | None:
        """Get team by abbreviation.

        Args:
            session: Database session
            abbreviation: Team abbreviation

        Returns:
            TeamModel instance or None if not found
        """
        return session.query(TeamModel).filter(TeamModel.abbreviation == abbreviation).first()

    def get_all_teams(self, session: Session) -> list[TeamModel]:
        """Get all teams.

        Args:
            session: Database session

        Returns:
            List of all TeamModel instances
        """
        return session.query(TeamModel).all()

    def get_all_players(self, session: Session) -> list[PlayerModel]:
        """Get all players.

        Args:
            session: Database session

        Returns:
            List of all PlayerModel instances
        """
        return session.query(PlayerModel).all()

    def count_records(self, session: Session) -> dict[str, int]:
        """Count records in each table.

        Args:
            session: Database session

        Returns:
            Dictionary with counts for each table
        """
        return {
            "teams": session.query(TeamModel).count(),
            "players": session.query(PlayerModel).count(),
            "player_stats": session.query(PlayerStatsModel).count(),
        }
