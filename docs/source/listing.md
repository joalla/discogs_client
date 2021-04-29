# Marketplace listing

As an authenticated user you can add, edit and delete your own marketplace `Listing`s.

## Add new `Listing`

```python
from discogs_client import Condition, Status, Sort
# Add new listing
me.inventory.add_listing(
    release=15246519,                       # Also accepts Release object
    condition=Condition.MINT,               # condition set to 'Mint (M)'
    price=29.99,
    status=Status.DRAFT,                    # status set to 'Draft'
    sleeve_condition=Condition.NEAR_MINT    # sleeve condition set to 'Near Mint (NM or M-)'
)
```

## Update `Listing`

Get the most expensive listing and update its price.

```python
inventory = me.inventory    # Get up to date inventory
inventory.sort(             # Sort by price in descending order
    Sort.By.PRICE,          # == 'price'
    Sort.Order.DESCENDING)  # == 'desc'
listing = inventory[0]      # Get the first item, i.e. most expensive
listing.price = 34.99       # Update its price
listing.save()              # Save changes made to listing
```

## Delete `Listing`

Instantiate a listing object as descibed in the previous example and call

```python
listing.delete()
```

to remove it.