# Marketplace listing

As an authenticated user you can add, edit and delete your own marketplace
`Listing`s.

## Add

```python
from discogs_client import Client, Condition, Status, Sort

d = Client('user-agent', user_token='my_user_token')
me = d.identity()

me.inventory.add_listing(
    release=15246519,                       # Also accepts an Release object
    condition=Condition.MINT,               # condition set to 'Mint (M)'
    price=29.99,
    status=Status.DRAFT,                    # status set to 'Draft'
    sleeve_condition=Condition.NEAR_MINT    # sleeve condition set to 'Near Mint (NM or M-)'
)
```

See the module documentation for possible values of condition
{class}`discogs_client.utils.Condition` and status
{class}`discogs_client.utils.Status`.


## Update

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

See the module documentation for possible values of sort criteria and sort
order {class}`discogs_client.utils.Sort`.

## Delete

Instantiate a `Listing` object as described in the previous example and call

```python
listing.delete()
```

to remove it.

## More information

View the module documentation at {class}`discogs_client.models.Inventory` and
{class}`discogs_client.models.Listing`