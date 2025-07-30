# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Honeybee-Energy-Ref properties for Honeybee-Energy OpaqueConstruction Objects"""

from copy import copy
from uuid import uuid4

try:
    from typing import Any
except Exception:
    pass  # IronPython 2.7

try:
    from honeybee_energy_ref.document_ref import DocumentReference
    from honeybee_energy_ref.image_ref import ImageReference
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ref:\n\t{}".format(e))


class HBObjwithDocRef_FromDictError(Exception):
    def __init__(self, _expected_types, _input_type):
        self.msg = 'Error: Expected type of "{}". Got: {}'.format(_expected_types, _input_type)
        super(HBObjwithDocRef_FromDictError, self).__init__(self.msg)


class _HBObjectWithReferences(object):
    """Honeybee Object with References for Documents and Images."""

    def __init__(self, _host=None):
        # type: (Any) -> None
        self._host = _host
        self.identifier = "rfs" + str(uuid4())[:8]
        self._document_refs = []  # type: list[DocumentReference]
        self._image_refs = []  # type: list[ImageReference]
        self._uris = []  # type: list[str]
        self.user_data = {}
        self._locked = True

    @property
    def host(self):
        # type: () -> Any  
        return self._host

    @property
    def host_name(self):
        # type: () -> str
        return getattr(self.host, "display_name", self.host.__class__.__name__) if self.host else "No Host"

    @property
    def document_refs(self):
        # type: () -> list[DocumentReference]
        """List of documents (pdf, etc) associated with the object."""
        return self._document_refs

    @property
    def image_refs(self):
        # type: () -> list[ImageReference]
        """List of any photos associated with the object."""
        return self._image_refs

    @property
    def uris(self):
        # type: () -> list[str]
        """List of URIs associated with the object."""
        return self._uris

    def add_document_ref(self, _document_ref):
        # type: (DocumentReference) -> None
        """Add a datasheet to the object.

        Arguments:
        ----------
            * _document_ref (DocumentReference): The document reference object to add.
        """

        if not isinstance(_document_ref, DocumentReference):
            raise TypeError("document must be an instance of DocumentReference.")
        if self._locked:
            raise AttributeError(
                "Cannot add datasheet to a locked {} on {}. Unlock the object first and"
                "copy to avoid modifying the object multiple times.".format(self.__class__.__name__, self.host_name)
            )
        self._document_refs.append(_document_ref)

    def add_image_ref(self, _image_ref):
        # type: (ImageReference) -> None
        """Add a new photo DocumentReference to the object.

        Arguments:
        ----------
            * _image_ref (ImageReference): The Image reference object to add.
        """

        if not isinstance(_image_ref, ImageReference):
            raise TypeError("image must be an instance of ImageReference.")
        if self._locked:
            raise AttributeError(
                "Cannot add photo to a locked {} on {}. Unlock the object first and"
                "copy to avoid modifying the object multiple times.".format(self.__class__.__name__, self.host_name)
            )
        self._image_refs.append(_image_ref)

    def add_uri(self, _uri):
        # type: (str) -> None
        """Add a URI to the object.

        Arguments:
        ----------
            * _uri (str): The URI to add.
        """

        if not isinstance(_uri, str):
            raise TypeError("URI must be a string. Got: {}".format(type(_uri).__name__))
        if self._locked:
            raise AttributeError(
                "Cannot add URI to a locked {} on {}. Unlock the object first and"
                "copy to avoid modifying the object multiple times.".format(self.__class__.__name__, self.host_name)
            )
        self._uris.append(_uri)

    def duplicate(self, new_host=None):
        # type: (Any) -> _HBObjectWithReferences
        """Duplicate this object with a new host.

        Arguments:
        ----------
            * new_host (Any): The new host for the duplicated object.

        Returns:
        --------
            * The duplicated object.
        """

        return self.__copy__(new_host)

    def __copy__(self, new_host=None):
        # type: (Any) -> _HBObjectWithReferences
        host = new_host or self.host
        new_obj = self.__class__(host)

        new_obj.unlock()

        new_obj.identifier = self.identifier
        new_obj._document_refs = [d.duplicate() for d in self._document_refs]
        new_obj._image_refs = [d.duplicate() for d in self._image_refs]
        new_obj._uris = [copy(uri) for uri in self._uris]  # Copy the list of URIs
        new_obj.user_data = copy(self.user_data)  # Copy user data

        new_obj.lock()

        return new_obj

    def to_dict(self, abridged=False):
        # type: (bool) -> dict
        """Return a dictionary representation of the object.

        Arguments:
        ----------
            * abridged (bool): Default=False. Set to True to return an abridged version of the object.

        Returns:
        --------
            * (dict): A dictionary representation of the object.
        """

        d = {}
        if abridged:
            d["type"] = "_HBObjectWithReferencesAbridged"
        else:
            d["type"] = "_HBObjectWithReferences"

        d["identifier"] = self.identifier
        d["document_refs"] = [ds.to_dict() for ds in self.document_refs]
        d["image_refs"] = [sp.to_dict() for sp in self.image_refs]
        d["uris"] = self.uris
        d["user_data"] = self.user_data

        return {"ref": d}

    @classmethod
    def from_dict(cls, _input_dict, _host):
        # type: (dict, Any) -> _HBObjectWithReferences
        """Create an object from a dictionary.

        Arguments:
        ----------
            * _input_dict (dict): The dictionary to create the object from.
            * _host (Any): The host for the new object.

        Returns:
        --------
            * The new object.
        """

        valid_types = ("_HBObjectWithReferencesAbridged", "_HBObjectWithReferences")
        if _input_dict["type"] not in valid_types:
            raise HBObjwithDocRef_FromDictError(valid_types, _input_dict["type"])

        new_obj = cls(_host)
        new_obj.unlock()

        new_obj.identifier = _input_dict.get("identifier", "rfs" + str(uuid4())[:8])

        for r in _input_dict.get("document_refs", []):
            new_obj.add_document_ref(DocumentReference.from_dict(r))

        for r in _input_dict.get("image_refs", []):
            new_obj.add_image_ref(ImageReference.from_dict(r))

        for uri in _input_dict.get("uris", []):
            new_obj.add_uri(uri)
        
        new_obj.user_data = _input_dict.get("user_data", {})

        new_obj.lock()

        return new_obj

    def lock(self):
        self._locked = True

    def unlock(self):
        self._locked = False

    def __eq__(self, other):
        # type: (object) -> bool
        """Check equality with another object.

        Arguments:
        ----------
            * other (object): The object to compare with.

        Returns:
        --------
            * (bool): True if the objects are equal, False otherwise.
        """
        if not isinstance(other, _HBObjectWithReferences):
            return False

        return (
            self.identifier == other.identifier
            and self.document_refs == other.document_refs
            and self.image_refs == other.image_refs
            and self.uris == other.uris
        )

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "{}(identifier={}, document_refs=[{}], image_refs=[{}], uris=[{}])".format(
            self.__class__.__name__, self.identifier, len(self.document_refs), len(self.image_refs), len(self.uris)
        )

    def ToString(self):
        return str(self)
