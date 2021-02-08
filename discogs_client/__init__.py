__version_info__ = 2, 2, 2
__version__ = '2.2.2'

from discogs_client.client import Client
from discogs_client.models import Artist, Release, Master, Label, User, \
    Listing, Track, Price, Video, List, ListItem, Inventory, Wantlist, \
    WantlistItem, CollectionItemInstance, CollectionFolder, Order, OrderMessage, OrderMessagesList
from discogs_client.utils import Condition, Sort, Status
