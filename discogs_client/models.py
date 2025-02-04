from discogs_client.exceptions import HTTPError
from discogs_client.utils import parse_timestamp, update_qs, omit_none


class SimpleFieldDescriptor:
    """
    An attribute that determines its value using the object's fetch() method.

    If transform is a callable, the value will be passed through transform when
    read. Useful for strings that should be ints, parsing timestamps, etc.

    Shorthand for:

        @property
        def foo(self):
            return self.fetch('foo')
    """
    def __init__(self, name, writable=False, transform=None):
        self.name = name
        self.writable = writable
        self.transform = transform

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = instance.fetch(self.name)
        if self.transform:
            value = self.transform(value)
        return value

    def __set__(self, instance, value):
        if self.writable:
            instance.changes[self.name] = value
            return
        raise AttributeError("can't set attribute")


class ObjectFieldDescriptor:
    """
    An attribute that determines its value using the object's fetch() method,
    and passes the resulting value through an APIObject.

    If optional = True, the value will be None (rather than an APIObject
    instance) if the key is missing from the response.

    If as_id = True, the value is treated as an ID for the new APIObject rather
    than a partial dict of the APIObject.

    Shorthand for:

        @property
        def baz(self):
            return BazClass(self.client, self.fetch('baz'))
    """
    def __init__(self, name, class_name, optional=False, as_id=False):
        self.name = name
        self.class_name = class_name
        self.optional = optional
        self.as_id = as_id

    def __get__(self, instance, owner):
        if instance is None:
            return self
        wrapper_class = CLASS_MAP[self.class_name.lower()]
        response_dict = instance.fetch(self.name)
        if self.optional and not response_dict:
            return None
        if self.as_id:
            # Response_dict wasn't really a dict. Make it so.
            response_dict = {'id': response_dict}
        return wrapper_class(instance.client, response_dict)

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")


class ListFieldDescriptor:
    """
    An attribute that determines its value using the object's fetch() method,
    and passes each item in the resulting list through an APIObject.

    Shorthand for:

        @property
        def bar(self):
            return [BarClass(self.client, d) for d in self.fetch('bar', [])]
    """
    def __init__(self, name, class_name):
        self.name = name
        self.class_name = class_name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        wrapper_class = CLASS_MAP[self.class_name.lower()]
        return [wrapper_class(instance.client, d) for d in instance.fetch(self.name, [])]

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")


class ObjectCollectionDescriptor:
    """
    An attribute that determines its value by fetching a URL to a paginated
    list of related objects, and passes each item in the resulting list through
    an APIObject.

    Shorthand for:

        @property
        def frozzes(self):
            return PaginatedList(self.client, self.fetch('frozzes_url'), 'frozzes', FrozClass)
    """
    def __init__(self, name, class_name, url_key=None, list_class=None):
        self.name = name
        self.class_name = class_name

        if url_key is None:
            url_key = name + '_url'
        self.url_key = url_key

        if list_class is None:
            list_class = PaginatedList
        self.list_class = list_class

    def __get__(self, instance, owner):
        if instance is None:
            return self
        wrapper_class = CLASS_MAP[self.class_name.lower()]
        return self.list_class(instance.client, instance.fetch(self.url_key), self.name, wrapper_class)

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")


class Field:
    """
    A placeholder for a descriptor. Is transformed into a descriptor by the
    APIObjectMeta metaclass when the APIObject classes are created.
    """
    _descriptor_class = None

    def __init__(self, *args, **kwargs):
        self.key = kwargs.pop('key', None)
        self.args = args
        self.kwargs = kwargs

    def to_descriptor(self, attr_name):
        return self._descriptor_class(self.key or attr_name, *self.args, **self.kwargs)


class SimpleField(Field):
    """A field that just returns the value of a given JSON key."""
    _descriptor_class = SimpleFieldDescriptor


class ListField(Field):
    """A field that returns a list of APIObjects."""
    _descriptor_class = ListFieldDescriptor


class ObjectField(Field):
    """A field that returns a single APIObject."""
    _descriptor_class = ObjectFieldDescriptor


class ObjectCollection(Field):
    """A field that returns a paginated list of APIObjects."""
    _descriptor_class = ObjectCollectionDescriptor


class APIObjectMeta(type):
    def __new__(cls, name, bases, namespace):
        for k, v in namespace.items():
            if isinstance(v, Field):
                namespace[k] = v.to_descriptor(k)
        return super(APIObjectMeta, cls).__new__(cls, name, bases, namespace)


class APIObject(metaclass=APIObjectMeta):
    pass


class PrimaryAPIObject(APIObject):
    """A first-order API object that has a canonical endpoint of its own."""
    def __init__(self, client, dict_):
        self.data = dict_
        self.client = client
        self._known_invalid_keys = []
        self.changes = {}
        self.previous_request = None

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        equal = self.__eq__(other)
        return NotImplemented if equal is NotImplemented else not equal

    def refresh(self):
        if self.data.get('resource_url'):
            data = self.client._get(self.data['resource_url'])
            self.data.update(data)
            self.changes = {}
            self.previous_request = self.data.get('resource_url')

    def save(self):
        if self.data.get('resource_url'):
            # TODO: This should be PATCH
            self.client._post(self.data['resource_url'], self.changes)

            # Refresh the object, in case there were side-effects
            self.refresh()

    def delete(self):
        if self.data.get('resource_url'):
            self.client._delete(self.data['resource_url'])

    def fetch(self, key, default=None):
        if key in self._known_invalid_keys:
            return default

        try:
            # First, look in the cache of pending changes
            return self.changes[key]
        except KeyError:
            pass

        try:
            # Next, look in the potentially incomplete local cache
            return self.data[key]
        except KeyError:
            pass

        # Object already refreshed from resource_url
        # return default to prevent an unnecessary API call
        if self.data.get('resource_url') == self.previous_request:
            self._known_invalid_keys.append(key)
            return default

        # Now refresh the object from its resource_url.
        # The key might exist but not be in our cache.
        self.refresh()

        try:
            return self.data[key]
        except:
            self._known_invalid_keys.append(key)
            return default


# This is terribly cheesy, but makes the client API more consistent
class SecondaryAPIObject(APIObject):
    """
    An object that wraps parts of a response and doesn't have its own
    endpoint.
    """
    def __init__(self, client, dict_):
        self.client = client
        self.data = dict_

    def fetch(self, key, default=None):
        return self.data.get(key, default)


class BasePaginatedResponse:
    """Base class for lists of objects spread across many URLs."""
    def __init__(self, client, url):
        self.client = client
        self.url = url
        self._num_pages = None
        self._num_items = None
        self._pages = {}
        self._per_page = 50
        self._list_key = 'items'
        self._sort_key = None
        self._sort_order = 'asc'
        self._filters = {}

    @property
    def per_page(self):
        return self._per_page

    @per_page.setter
    def per_page(self, value):
        self._per_page = value
        self._invalidate()

    def _invalidate(self):
        self._pages = {}
        self._num_pages = None
        self._num_items = None

    def _load_pagination_info(self):
        data = self.client._get(self._url_for_page(1))
        self._pages[1] = [
            self._transform(item) for item in data[self._list_key]
        ]
        self._num_pages = data['pagination']['pages']
        self._num_items = data['pagination']['items']

    def _url_for_page(self, page):
        base_qs = {
            'page': page,
            'per_page': self._per_page,
        }

        if self._sort_key is not None:
            base_qs.update({
                'sort': self._sort_key,
                'sort_order': self._sort_order,
            })

        base_qs.update(self._filters)

        return update_qs(self.url, base_qs)

    def sort(self, key, order='asc'):
        if order not in ('asc', 'desc'):
            raise ValueError("Order must be one of 'asc', 'desc'")
        self._sort_key = key
        self._sort_order = order
        self._invalidate()
        return self

    def filter(self, **kwargs):
        self._filters = kwargs
        self._invalidate()
        return self

    @property
    def pages(self):
        if self._num_pages is None:
            self._load_pagination_info()
        return self._num_pages

    @property
    def count(self):
        if self._num_items is None:
            self._load_pagination_info()
        return self._num_items

    def page(self, index):
        if index not in self._pages:
            data = self.client._get(self._url_for_page(index))
            self._pages[index] = [
                self._transform(item) for item in data[self._list_key]
            ]
        return self._pages[index]

    def _transform(self, item):
        return item

    def __getitem__(self, index):
        page_index = index // self.per_page + 1
        offset = index % self.per_page

        try:
            page = self.page(page_index)
        except HTTPError as e:
            if e.status_code == 404:
                raise IndexError(e.msg)
            else:
                raise

        return page[offset]

    def __len__(self):
        return self.count

    def __iter__(self):
        for i in range(1, self.pages + 1):
            page = self.page(i)
            for item in page:
                yield item


class PaginatedList(BasePaginatedResponse):
    """A paginated list of objects of a particular class."""
    def __init__(self, client, url, key, class_):
        super(PaginatedList, self).__init__(client, url)
        self._list_key = key
        self.class_ = class_

    def _transform(self, item):
        return self.class_(self.client, item)


class Wantlist(PaginatedList):
    def add(self, release, notes=None, notes_public=None, rating=None):
        release_id = release.id if isinstance(release, Release) else release
        data = {
            'release_id': str(release_id),
            'notes': notes,
            'notes_public': notes_public,
            'rating': rating,
        }
        self.client._put(self.url + '/' + str(release_id), omit_none(data))
        self._invalidate()

    def remove(self, release):
        release_id = release.id if isinstance(release, Release) else release
        self.client._delete(self.url + '/' + str(release_id))
        self._invalidate()


class Inventory(PaginatedList):
    def add_listing(self, release, condition, price, status, sleeve_condition=None,
                    comments=None, allow_offers=None, external_id=None, location=None,
                    weight=None, format_quantity=None):
        release_id = release.id if isinstance(release, Release) else release
        data = {
            "release_id": str(release_id),
            "condition": condition,
            "sleeve_condition": sleeve_condition,
            "price": price,
            "comments": comments,
            "allow_offers": allow_offers,
            "status": status,
            "external_id": external_id,
            "location": location,
            "weight": weight,
            "format_quantity": format_quantity,
        }
        self.client._post(self.client._base_url + '/marketplace/listings', omit_none(data))
        self._invalidate()


class OrderMessagesList(PaginatedList):
    def add(self, message=None, status=None, email_buyer=True, email_seller=False):
        data = {
            'message': message,
            'status': status,
            'email_buyer': email_buyer,
            'email_seller': email_seller,
        }
        self.client._post(self.url, omit_none(data))
        self._invalidate()


class MixedPaginatedList(BasePaginatedResponse):
    """A paginated list of objects identified by their type parameter."""
    def __init__(self, client, url, key):
        super(MixedPaginatedList, self).__init__(client, url)
        self._list_key = key

    def _transform(self, item):
        # In some cases, we want to map the 'title' key we get back in search
        # results to 'name'. This way, you can repr() a page of search results
        # without making 50 requests.
        if item['type'] in ('label', 'artist'):
            item['name'] = item['title']

        return CLASS_MAP[item['type']](self.client, item)


class Artist(PrimaryAPIObject):
    """An object describing an artist"""
    id = SimpleField()  #:
    name = SimpleField()  #:
    real_name = SimpleField(key='realname')  #:
    images = SimpleField()  #:
    profile = SimpleField()  #:
    data_quality = SimpleField()  #:
    name_variations = SimpleField(key='namevariations')  #:
    url = SimpleField(key='uri')  #:
    urls = SimpleField()  #:
    aliases = ListField('Artist')  #:
    members = ListField('Artist')  #:
    groups = ListField('Artist')  #:
    #: This attribute is only populated when an ``Artist`` object is requested
    #: via the ``artists`` list of a ``Release`` object, and if it is a
    #: multi-artist release. Usually only the first ``Artist`` object in the
    #: ``artists`` list contains a keyword such as "And", "Feat", "Vs", or
    #: similar. This keyword could be used to combine artists together into a
    #: single string, for example: "DJ ABC Feat MC Z". Also check out the
    #: ``artists_sort`` attribute of a ``Release`` object.
    join = SimpleField()
    #: This attribute is only present when an ``Artist`` object is part of a
    #: ``credits`` list of a ``Release`` object.
    role = SimpleField()
    
    def __init__(self, client, dict_):
        super(Artist, self).__init__(client, dict_)
        self.data['resource_url'] = '{0}/artists/{1}'.format(client._base_url, dict_['id'])

    @property
    def releases(self):
        return MixedPaginatedList(self.client, self.fetch('releases_url'), 'releases')

    def __repr__(self):
        return '<Artist {0!r} {1!r}>'.format(self.id, self.name)


class Release(PrimaryAPIObject):
    """An object describing a Discogs release."""
    id = SimpleField()  #:
    title = SimpleField()  #:
    year = SimpleField()  #:
    thumb = SimpleField()  #:
    data_quality = SimpleField()  #:
    status = SimpleField()  #:
    genres = SimpleField()  #:
    images = SimpleField()  #:
    country = SimpleField()  #:
    notes = SimpleField()  #:
    formats = SimpleField()  #:
    styles = SimpleField()  #:
    url = SimpleField(key='uri')  #:
    videos = ListField('Video')  #:
    tracklist = ListField('Track')  #:
    #: A list of ``Artist`` objects. Even though a release could be by one
    #: artist only, this will always be a list.
    artists = ListField('Artist')
    #: On multi-artist releases this attribute provides a string containing
    #: artists combinend together with a keyword such as "And", "Feat", "Vs",
    #: or similar, for example "DJ ABC Feat MC Z". Also check out at the
    #: ``join`` attribute of an ``Artist`` object.
    artists_sort = SimpleField()
    credits = ListField('Artist', key='extraartists')  #:
    #: A list of ``Label`` objects. Even though a release could have been
    #: published on one label only, this will always be a list.
    labels = ListField('Label')
    companies = ListField('Label')  #:
    community = ObjectField("communitydetails")  #:

    def __init__(self, client, dict_):
        super(Release, self).__init__(client, dict_)
        self.data['resource_url'] = '{0}/releases/{1}'.format(client._base_url, dict_['id'])

    @property
    def master(self):
        master_id = self.fetch('master_id')
        if master_id:
            return Master(self.client, {'id': master_id})
        else:
            return None

    @property
    def marketplace_stats(self):
        release_id = self.fetch('id')
        if release_id:
            return MarketplaceStats(self.client, {'id': release_id})
        else:
            return None

    @property
    def price_suggestions(self):
        release_id = self.fetch('id')
        if release_id:
            return PriceSuggestions(self.client, {'id': release_id})
        else:
            return None

    def __repr__(self):
        return '<Release {0!r} {1!r}>'.format(self.id, self.title)


class MarketplaceStats(PrimaryAPIObject):
    num_for_sale = SimpleField()  #:
    blocked_from_sale = SimpleField()  #:
    lowest_price = ObjectField('Price')  #:

    def __init__(self, client, dict_):
        super(MarketplaceStats, self).__init__(client, dict_)
        self.data['resource_url'] = '{0}/marketplace/stats/{1}'.format(client._base_url, dict_['id'])

    def __repr__(self):
        return '<MarketplaceStats {0!r} for sale>'.format(self.num_for_sale)


class PriceSuggestions(PrimaryAPIObject):
    very_good = ObjectField("Price", key="Very Good (VG)")  #:
    good_plus = ObjectField("Price", key="Good Plus (G+)")  #:
    near_mint = ObjectField("Price", key="Near Mint (NM or M-)")  #:
    good = ObjectField("Price", key="Good (G)")  #:
    very_good_plus = ObjectField("Price", key="Very Good Plus (VG+)")  #:
    mint = ObjectField("Price", key="Mint (M)")  #:
    fair = ObjectField("Price", key="Fair (F)")  #:
    poor = ObjectField("Price", key="Poor (P)")  #:

    def __init__(self, client, dict_):
        super(PriceSuggestions, self).__init__(client, dict_)
        self.data['resource_url'] = '{0}/marketplace/price_suggestions/{1}'.format(client._base_url, dict_['id'])

    def __repr__(self) -> str:
        return '<PriceSuggestions Price for Mint (M) is {0!r}>'.format(self.mint)


class Master(PrimaryAPIObject):
    id = SimpleField()  #:
    title = SimpleField()  #:
    data_quality = SimpleField()  #:
    styles = SimpleField()  #:
    year = SimpleField()  #:
    genres = SimpleField()  #:
    images = SimpleField()  #:
    url = SimpleField(key='uri')  #:
    videos = ListField('Video')  #:
    tracklist = ListField('Track')  #:
    main_release = ObjectField('Release', as_id=True)  #:
    versions = ObjectCollection('Release')  #:

    def __init__(self, client, dict_):
        super(Master, self).__init__(client, dict_)
        self.data['resource_url'] = '{0}/masters/{1}'.format(client._base_url, dict_['id'])

    def __repr__(self):
        return '<Master {0!r} {1!r}>'.format(self.id, self.title)


class Label(PrimaryAPIObject):
    id = SimpleField()  #:
    name = SimpleField()  #:
    profile = SimpleField()  #:
    urls = SimpleField()  #:
    images = SimpleField()  #:
    contact_info = SimpleField()  #:
    data_quality = SimpleField()  #:
    url = SimpleField(key='uri')  #:
    sublabels = ListField('Label')  #:
    parent_label = ObjectField('Label', optional=True)  #:
    releases = ObjectCollection('Release')  #:
    #: The "catalog number" attribute is only populated when a ``Label``
    #: object is fetched via a ``Release`` object, otherwise it is None.
    catno = SimpleField()

    def __init__(self, client, dict_):
        super(Label, self).__init__(client, dict_)
        self.data['resource_url'] = '{0}/labels/{1}'.format(client._base_url, dict_['id'])

    def __repr__(self):
        return '<Label {0!r} {1!r}>'.format(self.id, self.name)


class User(PrimaryAPIObject):
    id = SimpleField()  #:
    username = SimpleField()  #:
    releases_contributed = SimpleField()  #:
    num_collection = SimpleField()  #:
    num_wantlist = SimpleField()  #:
    num_lists = SimpleField()  #:
    rank = SimpleField()  #:
    rating_avg = SimpleField()  #:
    url = SimpleField(key='uri')  #:
    name = SimpleField(writable=True)  #:
    profile = SimpleField(writable=True)  #:
    location = SimpleField(writable=True)  #:
    home_page = SimpleField(writable=True)  #:
    registered = SimpleField(transform=parse_timestamp)  #:
    inventory = ObjectCollection('Listing', key='listings', url_key='inventory_url', list_class=Inventory)  #:
    wantlist = ObjectCollection('WantlistItem', key='wants', url_key='wantlist_url', list_class=Wantlist)  #:

    def __init__(self, client, dict_):
        super(User, self).__init__(client, dict_)
        self.data['resource_url'] = '{0}/users/{1}'.format(client._base_url, dict_['username'])

    @property
    def orders(self):
        return PaginatedList(self.client, self.client._base_url + '/marketplace/orders', 'orders', Order)

    @property
    def lists(self):
        return PaginatedList(self.client, self.fetch('resource_url') + '/lists', 'lists', List)

    @property
    def collection_folders(self):
        resp = self.client._get(self.fetch('collection_folders_url'))
        return [CollectionFolder(self.client, d) for d in resp['folders']]

    def collection_items(self, release):
        """Fetch collection items by release, accepts Release object or release id

        Parameters
        ----------
        release : Release or int

        Returns
        -------
        PaginatedList
            PaginatedList of CollectionItemInstance objects
        """

        release_id = release.id if isinstance(release, Release) else release
        return PaginatedList(self.client,self.fetch('resource_url') + "/collection/releases/{}".format(release_id) , "releases", CollectionItemInstance)

    @property
    def collection_value(self):
        resp = self.client._get(f"{self.fetch('resource_url')}/collection/value")
        return CollectionValue(self.client, resp)

    def __repr__(self):
        return '<User {0!r} {1!r}>'.format(self.id, self.username)


class WantlistItem(PrimaryAPIObject):
    id = SimpleField()  #:
    rating = SimpleField(writable=True)  #:
    notes = SimpleField(writable=True)  #:
    notes_public = SimpleField(writable=True)  #:
    release = ObjectField('Release', key='basic_information')  #:

    def __init__(self, client, dict_):
        super(WantlistItem, self).__init__(client, dict_)

    def __repr__(self):
        return '<WantlistItem {0!r} {1!r}>'.format(self.id, self.release.title)


# TODO: folder_id should be a Folder object; needs folder_url
# TODO: notes should be first-order (somehow); needs resource_url
class CollectionItemInstance(PrimaryAPIObject):
    id = SimpleField()  #:
    instance_id = SimpleField()  #:
    rating = SimpleField()  #:
    folder_id = SimpleField()  #:
    notes = SimpleField()  #:
    date_added = SimpleField(transform=parse_timestamp)  #:
    release = ObjectField('Release', key='basic_information')  #:

    def __init__(self, client, dict_):
        super(CollectionItemInstance, self).__init__(client, dict_)

    def __repr__(self):
        return '<CollectionItemInstance {0!r} {1!r}>'.format(self.id, self.release.title)


class CollectionValue(PrimaryAPIObject):
    maximum = SimpleField()  #:
    median = SimpleField()  #:
    minimum = SimpleField()  #:

    def __init__(self, client, dict_):
        super(CollectionValue, self).__init__(client, dict_)

    def __repr__(self):
        return f"<CollectionValue {self.median}>"


class CollectionFolder(PrimaryAPIObject):
    id = SimpleField()  #:
    name = SimpleField()  #:
    count = SimpleField()  #:

    def __init__(self, client, dict_):
        super(CollectionFolder, self).__init__(client, dict_)

    @property
    def releases(self):
        # TODO: Needs releases_url
        return PaginatedList(self.client, self.fetch('resource_url') + '/releases', 'releases', CollectionItemInstance)

    def add_release(self, release):
        release_id = release.id if isinstance(release, Release) else release
        add_release_url = self.fetch('resource_url') + '/releases/{}'.format(release_id)
        self.client._post(add_release_url, None)

    def remove_release(self, instance):
        """Remove a collection item entirely.
        """
        if not isinstance(instance, CollectionItemInstance):
            raise TypeError('instance must be of type CollectionItemInstance')
        instance_url = self.fetch('resource_url') + '/releases/{0}/instances/{1}'.format(instance.id, instance.instance_id)
        self.client._delete(instance_url)

    def move_release(self, instance, target_folder_id):
        """Move a collection item to another folder.

        Moving to folder id 1 moves to the "Uncategorized" folder.
        """
        if not isinstance(instance, CollectionItemInstance):
            raise TypeError('instance must be of type CollectionItemInstance')
        instance_url = self.fetch('resource_url') + '/releases/{0}/instances/{1}'.format(instance.id, instance.instance_id)
        data = {'folder_id': target_folder_id}
        self.client._post(instance_url, data)

    def uncategorize_release(self, instance):
        """Move a collection item to the "Uncategorized" folder.
        """
        self.move_release(instance, 1)

    def __repr__(self):
        return '<CollectionFolder {0!r} {1!r}>'.format(self.id, self.name)


class List(PrimaryAPIObject):
    id = SimpleField()  #:
    name = SimpleField()  #:
    description = SimpleField()  #:
    public = SimpleField()  #:
    url = SimpleField(key='uri')  #:
    date_changed = SimpleField(transform=parse_timestamp)  #:
    date_added = SimpleField(transform=parse_timestamp)  #:
    items = ListField('ListItem')  #:

    def __init__(self, client, dict_):
        super(List, self).__init__(client, dict_)
        self.data['resource_url'] = '{0}/lists/{1}'.format(client._base_url, dict_['id'])

    def __repr__(self):
        return '<List {0!r} {1!r}>'.format(self.id, self.name)


class Listing(PrimaryAPIObject):
    id = SimpleField()  #:
    status = SimpleField(writable=True)  #:
    allow_offers = SimpleField(writable=True)  #:
    condition = SimpleField(writable=True)  #:
    sleeve_condition = SimpleField(writable=True)  #:
    ships_from = SimpleField()  #:
    comments = SimpleField(writable=True)  #:
    audio = SimpleField()  #:
    url = SimpleField(key='uri')  #:
    release = ObjectField('Release')  #:
    seller = ObjectField('User')  #:
    posted = SimpleField(transform=parse_timestamp)  #:
    weight = SimpleField(writable=True)  #:
    location = SimpleField(writable=True)  #:
    format_quantity = SimpleField(writable=True)  #:
    external_id = SimpleField(writable=True)  #:

    def __init__(self, client, dict_):
        super(Listing, self).__init__(client, dict_)
        self.data['resource_url'] = '{0}/marketplace/listings/{1}'.format(client._base_url, dict_['id'])

    @property
    def price(self):
        # Get unsaved price.value from changes
        if 'price' in self.changes:
            return Price(self.client, {
                'value': self.changes['price'],
                'currency': self.data['price']['currency']
            })
        return Price(self.client, self.fetch('price'))

    @price.setter
    def price(self, value):
        self.changes['price'] = value

    def __repr__(self):
        return '<Listing {0!r} {1!r}>'.format(self.id, self.release.data['description'])


class Order(PrimaryAPIObject):
    id = SimpleField()  #:
    next_status = SimpleField()  #:
    shipping_address = SimpleField()  #:
    additional_instructions = SimpleField()  #:
    url = SimpleField(key='uri')  #:
    status = SimpleField(writable=True)  #:
    fee = ObjectField('Price')  #:
    buyer = ObjectField('User')  #:
    seller = ObjectField('User')  #:
    created = SimpleField(transform=parse_timestamp)  #:
    last_activity = SimpleField(transform=parse_timestamp)  #:
    messages = ObjectCollection('OrderMessage', list_class=OrderMessagesList)  #:
    items = ListField('Listing')  #:

    def __init__(self, client, dict_):
        super(Order, self).__init__(client, dict_)
        self.data['resource_url'] = '{0}/marketplace/orders/{1}'.format(client._base_url, dict_['id'])

    # Setting shipping is a little weird -- you can't change the
    # currency, and you use the 'shipping' key instead of 'value'
    @property
    def shipping(self):
        return Price(self.client, self.fetch('shipping'))

    @shipping.setter
    def shipping(self, value):
        self.changes['shipping'] = value

    def __repr__(self):
        return '<Order {0!r}>'.format(self.id)


class OrderMessage(SecondaryAPIObject):
    subject = SimpleField()  #:
    message = SimpleField()  #:
    to = ObjectField('User')  #:
    order = ObjectField('Order')  #:
    timestamp = SimpleField(transform=parse_timestamp)  #:

    def __repr__(self):
        return '<OrderMessage to:{0!r}>'.format(self.to.username)


class Track(SecondaryAPIObject):
    duration = SimpleField()  #:
    position = SimpleField()  #:
    title = SimpleField()  #:
    artists = ListField('Artist')  #: FIXME could an artist in this list contain the "join" field as well?
    credits = ListField('Artist', key='extraartists')  #:

    def __repr__(self):
        return '<Track {0!r} {1!r}>'.format(self.position, self.title)


class Price(SecondaryAPIObject):
    currency = SimpleField()  #:
    value = SimpleField()  #:

    def __repr__(self):
        return '<Price {0!r} {1!r}>'.format(self.value, self.currency)


class Video(SecondaryAPIObject):
    duration = SimpleField()  #:
    embed = SimpleField()  #:
    title = SimpleField()  #:
    description = SimpleField()  #:
    url = SimpleField(key='uri')  #:

    def __repr__(self):
        return '<Video {0!r}>'.format(self.title)


class ListItem(SecondaryAPIObject):
    id = SimpleField()  #:
    comment = SimpleField()  #:
    display_title = SimpleField()  #:
    type = SimpleField()  #:
    image_url = SimpleField()  #:
    url = SimpleField(key='uri')  #:

    def __repr__(self):
        return '<ListItem {0!r}>'.format(self.id)


class CommunityDetails(SecondaryAPIObject):
    """
    An object that wraps the "community" data found in a :class:`.Release`
    object.
    """
    status = SimpleField()  #:
    data_quality = SimpleField()  #:
    want = SimpleField()  #:
    have = SimpleField()  #:
    rating = ObjectField('Rating')  #:
    contributors = ListField("User")  #:
    submitter = ObjectField("User")  #:

    def __repr__(self):
        return '<CommunityDetails want/have: {0!r}/{1!r}>'.format(self.want, self.have)


class Rating(SecondaryAPIObject):
    """
    An object that wraps the "community.rating" data found in a
    :class:`.Release` object.
    """
    count = SimpleField()  #:
    average = SimpleField()  #:

    def __repr__(self):
        return '<Rating avg: {0!r}>'.format(self.average)


CLASS_MAP = {
    'artist': Artist,
    'release': Release,
    'marketplacestats': MarketplaceStats,
    'pricesuggestions': PriceSuggestions,
    'master': Master,
    'label': Label,
    'price': Price,
    'video': Video,
    'track': Track,
    'user': User,
    'order': Order,
    'list': List,
    'listitem': ListItem,
    'listing': Listing,
    'wantlistitem': WantlistItem,
    'ordermessage': OrderMessage,
    'collectionvalue': CollectionValue,
    'communitydetails': CommunityDetails,
    'rating': Rating,
}
