# Assuming your Logger instance is imported like this
from loggerpython import Logger


def run_tests():

    Logger.warning("Memory usage is high.")

    # Set_loglevel will work from where it is placed it will not affect the previous logs
    Logger.set_loglevel("INFO")

    Logger.debug("This is a debug message.")
    Logger.info("System started successfully.")
    Logger.warning("Memory usage is high.")
    Logger.error("File not found.")
    Logger.error("Failed to connect to the database.")
    Logger.critical("System crash! Immediate action required.")


if __name__ == "__main__":
    run_tests()
