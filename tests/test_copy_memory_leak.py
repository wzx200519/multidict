import random
import string
import tracemalloc
import pytest
from multidict import MultiDict


def create_large_multidict():
    """Create a large MultiDict with 100,000 random key-value pairs."""
    md = MultiDict()
    for _ in range(100000):
        key = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        value = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        md[key] = value
    return md


def test_copy_no_memory_leak():
    """Test that MultiDict.copy() doesn't leak memory."""
    # Create the large multidict first
    large_md = create_large_multidict()
    
    # Start tracing memory allocations
    tracemalloc.start()
    
    # Take a snapshot before copy operations
    snapshot1 = tracemalloc.take_snapshot()
    
    # Perform 1000 copy operations
    copies = []
    for _ in range(1000):
        md_copy = large_md.copy()
        copies.append(md_copy)
    
    # Take a snapshot after copy operations
    snapshot2 = tracemalloc.take_snapshot()
    
    # Calculate memory usage
    stats1 = snapshot1.statistics('lineno')
    stats2 = snapshot2.statistics('lineno')
    
    # Get total memory usage before and after
    total1 = sum(stat.size for stat in stats1)
    total2 = sum(stat.size for stat in stats2)
    
    # Clear the copies to free memory
    copies.clear()
    
    # Stop tracing
    tracemalloc.stop()
    
    # Calculate memory growth percentage
    if total1 == 0:
        # If initial memory is 0, we can't calculate growth percentage
        # But this shouldn't happen with a large MultiDict
        assert total2 == 0, "Memory usage unexpectedly increased from 0"
    else:
        growth_percentage = ((total2 - total1) / total1) * 100
        assert growth_percentage < 5, f"Memory growth of {growth_percentage:.2f}% exceeds 5% threshold"
