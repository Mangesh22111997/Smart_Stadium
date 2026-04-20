"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""


from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize Limiter as a singleton to avoid circular imports
limiter = Limiter(key_func=get_remote_address)
