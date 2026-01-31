"""
Configuration file for the Heritage Horizon Backend
"""

import os

class Config:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    JSON_SORT_KEYS = False
    # Database
    DATABASE = "game_scores.db"
    # Flask
    FLASK_ENV = "production"

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = "development"

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE = "test_game_scores.db"

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = "production"

# Select config based on environment
config_name = os.getenv("FLASK_ENV", "development")
if config_name == "testing":
    config = TestingConfig()
elif config_name == "production":
    config = ProductionConfig()
else:
    config = DevelopmentConfig()
