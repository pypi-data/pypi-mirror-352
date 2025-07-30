# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from rapidfuzz.fuzz import ratio as fuzz_ratio
from rapidfuzz.fuzz import token_set_ratio


class NameItem:
    def __init__(self, source_name=None, name=None, form=None, url=None, rig=None):
        self.url = url
        self.source_name = source_name
        self.name = name
        self.form = form
        self.rig = rig

    def __str__(self):
        return '"' + '"\t"'.join([self.url or '', self.source_name or '', self.name or '', self.form or '', self.rig or '']) + '"'

    def __hash__(self):
        return hash(f'{self.url};;{self.source_name};;{self.name};;{self.form};;{self.rig}')

    def copy(self):
        return NameItem(url=self.url, source_name=self.source_name, name=self.name, form=self.form, rig=self.rig)

    @property
    def is_ignored(self):
        return self.form == 'ignore'


class NameIndex:
    def __init__(self, items=None):
        self._by_hash = {}  # hash: NameItem, primary inded
        self._by_url = {}  # url: NameItem
        # The rest are {attribute: [item1, item2, ...], name2: [item3, item4, ...]}
        self._by_source_name = {}
        self._by_name = {}
        self._by_form = {}
        self._by_rig = {}
        if items is not None:
            for item in items:
                self.add(item)

    def __len__(self):
        return len(self._by_hash)

    def __bool__(self):
        return len(self) > 0

    def __iter__(self):
        for item in self._by_hash.values():
            yield item

    @property
    def items(self):
        return [item for item in self._by_hash.values()]

    @items.setter
    def items(self, items):
        self._by_hash = {}
        self._by_url = {}
        self._by_source_name = {}
        self._by_name = {}
        self._by_form = {}
        self._by_rig = {}
        for item in items:
            self.add(item)

    @classmethod
    def read_tsv(cls, file_path):
        df = pd.read_csv(file_path, sep='\t', header=0, encoding='utf-8', dtype=str, na_values=None)
        df.replace([np.nan], [None], inplace=True)
        return cls(
            [NameItem(
                url=row['url'], source_name=row['source_name'], name=row['name'], form=row['form'], rig=row['rig'])
             for i, row in df.iterrows()])

    def write_tsv(self, file_path):
        df = pd.DataFrame(
            [[item.url, item.source_name, item.name, item.form, item.rig] for item in self.items],
            columns=['url', 'source_name', 'name', 'form', 'rig'])
        df.fillna('', inplace=True)
        df.sort_values(['name', 'rig'], inplace=True)
        df.to_csv(file_path, sep='\t', header=True, index=False, encoding='utf-8')

    def add(self, item):
        """Adds an item to index."""
        if hash(item) in self._by_hash:
            return
        self._by_hash[hash(item)] = item
        if item.url is not None:
            self._by_url[item.url] = item
        if item.source_name is not None:
            if item.source_name not in self._by_source_name:
                self._by_source_name[item.source_name] = []
            self._by_source_name[item.source_name].append(item)
        if item.name is not None:
            if item.name not in self._by_name:
                self._by_name[item.name] = []
            self._by_name[item.name].append(item)
        if item.form is not None:
            if item.form not in self._by_form:
                self._by_form[item.form] = []
            self._by_form[item.form].append(item)
        if item.rig is not None:
            if item.rig not in self._by_rig:
                self._by_rig[item.rig] = []
            self._by_rig[item.rig].append(item)

    def concat(self, name_index):
        """Merges another NameIndex to this."""
        for item in name_index.items:
            self.add(item)

    def update(self, item):
        """Updates all items which have the same URL as the given item

        Args:
            item: New value as NameItem

        Returns:
            None
        """
        if item.url is None:
            raise ValueError('Item doesn\'t have URL')
        if item.url not in self._by_url:
            return self.add(item)
        old_item = self._by_url[item.url]
        del self._by_url[item.url]
        # Move old item to new index locations where the attributes have changed
        if item.source_name != old_item.source_name:  # Source name has changed
            if old_item.source_name in self._by_source_name:
                self._by_source_name[old_item.source_name].remove(old_item)  # Remove from old index location
            old_item.source_name = item.source_name
            if item.source_name not in self._by_source_name:  # Init new index location if needed
                self._by_source_name[item.source_name] = []
            self._by_source_name[item.source_name].append(old_item)  # Add old item to new index location
        if item.name != old_item.name:
            if old_item.name in self._by_name:
                self._by_name[old_item.name].remove(old_item)
            old_item.name = item.name
            if item.name not in self._by_name:
                self._by_name[item.name] = []
            self._by_name[item.name].append(old_item)
        if item.form != old_item.form:
            if old_item.form in self._by_form:
                self._by_form[old_item.form].remove(old_item)
            old_item.form = item.form
            if item.form not in self._by_form:
                self._by_form[item.form] = []
            self._by_form[item.form].append(old_item)
        if item.rig != old_item.rig:
            if old_item.rig in self._by_rig:
                self._by_rig[old_item.rig].remove(old_item)
            old_item.rig = item.rig
            if item.rig not in self._by_rig:
                self._by_rig[item.rig] = []
            self._by_rig[item.rig].append(old_item)

    def remove(self, item):
        if hash(item) not in self._by_hash:
            return
        del self._by_hash[hash(item)]
        if item.url is not None and item.url in self._by_url:
            del self._by_url[item.url]
        if item.source_name is not None and item.source_name in self._by_source_name:
            del self._by_source_name[item.source_name]
        if item.name is not None and item.name in self._by_name:
            del self._by_name[item.name]
        if item.form is not None and item.form in self._by_form:
            del self._by_form[item.form]
        if item.rig is not None and item.rig in self._by_rig:
            del self._by_rig[item.rig]

    def find(self, url=None, source_name=None, name=None, form=None, rig=None):
        """Finds all items which match the given query parameters.

        Args:
            url: Measurement source URL
            source_name: Measurement name in the source
            name: Measurement name in AutoEq
            form: Measured item form (over-ear, in-ear or earbud)
            rig: Measurement rig used

        Returns:
            New NameIndex instance with the matching items
        """
        items = None
        if url is not None:
            if url not in self._by_url:
                return None
            items = {self._by_url[url]}
        if source_name is not None:
            if source_name not in self._by_source_name:
                return None
            by_source_name = set(self._by_source_name[source_name])
            items = items.intersection(by_source_name) if items is not None else by_source_name
        if name is not None:
            if name not in self._by_name:
                return None
            by_name = set(self._by_name[name])
            items = items.intersection(by_name) if items is not None else by_name
        if form is not None:
            if form not in self._by_form:
                return None
            by_form = set(self._by_form[form])
            items = items.intersection(by_form) if items is not None else by_form
        if rig is not None:
            if rig not in self._by_rig:
                return None
            by_rig = set(self._by_rig[rig])
            items = items.intersection(by_rig) if items is not None else by_rig
        return self.__class__(items)

    def find_one(self, **kwargs):
        results = self.find(**kwargs)
        if results:
            return results.items[0]

    def search_by_source_name(self, source_name, threshold=80):
        """Searches name index by source name with fuzzy matching.

        Args:
            source_name: Source name to search for
            threshold: Match threshold in 0 to 100 range with 100 being perfect match

        Returns:
            NameIndex object with matched items
        """
        matches = []
        for item in self.items:
            # Search with false name
            similarity_ratio = fuzz_ratio(item.source_name.lower(), source_name.lower())
            similarity_token_set_ratio = token_set_ratio(item.source_name.lower(), source_name.lower())
            if similarity_ratio > threshold or similarity_token_set_ratio > threshold:
                matches.append((item, similarity_ratio, similarity_token_set_ratio))

        # Sort by sum of both ratios
        matches = sorted(matches, key=lambda x: x[1] + x[2], reverse=True)
        return NameIndex([match[0] for match in matches])

    def search_by_name(self, name, threshold=80):
        """Searches name index by normalized name with fuzzy matching.

        Args:
            name: Normalized name to search for
            threshold: Match threshold in 0 to 100 range with 100 being perfect match

        Returns:
            NameIndex object with matched items
        """
        matches = []
        for item in self.items:
            # Search with false name
            similarity_ratio = fuzz_ratio(item.name.lower(), name.lower())
            similarity_token_set_ratio = token_set_ratio(item.name.lower(), name.lower())
            if similarity_ratio > threshold or similarity_token_set_ratio > threshold:
                matches.append((item, similarity_ratio, similarity_token_set_ratio))

        # Sort by sum of both ratios
        matches = sorted(matches, key=lambda x: x[1] + x[2], reverse=True)
        return NameIndex([match[0] for match in matches])
