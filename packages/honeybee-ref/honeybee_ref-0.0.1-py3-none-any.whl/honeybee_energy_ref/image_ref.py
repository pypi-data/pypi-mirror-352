# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Honeybee-Energy ImageReference Object for storing URIs of images related to the host object."""

from uuid import uuid4


class ImageReference(object):

    def __init__(self):
        # type: () -> None
        self.identifier = "img" + str(uuid4())[:8]
        self.thumbnail_image_uri = None  # type: str | None
        self.full_size_image_uri = None  # type: str | None

    def to_dict(self):
        # type: () -> dict
        """Return a dictionary representation of the object.

        Returns:
        --------
            * (dict): A dictionary representation of the object.
        """
        return {
            "identifier": self.identifier,
            "thumbnail_image_uri": self.thumbnail_image_uri,
            "full_size_image_uri": self.full_size_image_uri,
        }

    @classmethod
    def from_dict(cls, input_dict):
        # type: (dict) -> ImageReference
        """Create an object from a dictionary.

        Arguments:
        ----------
            * input_dict (dict): The dictionary to create the object from.

        Returns:
        --------
            * (ImageReference): The new object.
        """
        new_obj = cls()
        new_obj.identifier = input_dict.get("identifier", "img" + str(uuid4())[:8])
        new_obj.thumbnail_image_uri = input_dict.get("thumbnail_image_uri", None)
        new_obj.full_size_image_uri = input_dict.get("full_size_image_uri", None)
        return new_obj

    def duplicate(self):
        # type: () -> ImageReference
        """Duplicate this object.

        Returns:
        --------
            * (ImageReference): The duplicated object.
        """
        return self.__copy__()

    def __copy__(self):
        # type: () -> ImageReference
        """Create a copy of the object.

        Returns:
        --------
            * (ImageReference): The duplicated object.
        """
        new_obj = self.__class__()
        new_obj.identifier = self.identifier
        new_obj.thumbnail_image_uri = self.thumbnail_image_uri
        new_obj.full_size_image_uri = self.full_size_image_uri
        return new_obj

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
        if not isinstance(other, ImageReference):
            return False
        return (
            self.identifier == other.identifier and
            self.thumbnail_image_uri == other.thumbnail_image_uri and
            self.full_size_image_uri == other.full_size_image_uri
        )

    def __str__(self):
        # type: () -> str
        return "{}(identifier={}, thumbnail_image_uri={}, full_size_image_uri={})".format(
            self.__class__.__name__, self.identifier, self.thumbnail_image_uri, self.full_size_image_uri
        )

    def __repr__(self):
        # type: () -> str
        return self.__str__()

    def ToString(self):
        return str(self)
