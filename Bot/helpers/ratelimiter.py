from typing import Union  # Importing Union type for type hints
from pyrate_limiter import Duration, Limiter, Rate, BucketFullException  # Importing necessary classes from pyrate_limiter module

class RateLimiter:
    '''A class to handle rate limiting functionality.'''

    def __init__(self) -> None:
        '''
        Initialize a RateLimiter instance.

        The RateLimiter allows limiting the rate of requests.
        It sets up a Limiter object with predefined rates for different time durations.

        Rates:
        - 10 requests per second
        - 30 requests per minute
        - 1000 requests per hour
        - 10000 requests per day
        '''
        rates = [
            Rate(10, Duration.SECOND), # 10 requests per second
            Rate(30, Duration.MINUTE), # 30 requests per minute
            Rate(1000, Duration.HOUR), # 1000 requests per hour
            Rate(10000, Duration.DAY)  # 10000 requests per day
        ]
        self.limiter = Limiter(rates)  # Initializing the Limiter with the defined rates

    async def acquire(self, user_id: Union[int, str]) -> bool:
        '''
        Acquire a permit for the given user ID.

        Args:
            user_id (Union[int, str]): The ID of the user.

        Returns:
            bool: True if the permit was acquired (user exceeded rate limit), False otherwise.
        '''
        try:
            self.limiter.try_acquire(user_id)  # Try to acquire a permit for the user
            return False  # Permit acquired successfully, user not exceeding rate limit
        except BucketFullException:
            return True  # Permit not acquired, user exceeded rate limit