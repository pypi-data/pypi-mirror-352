from itertools import tee
import numpy as np
import re



class Tokens:
    r"""
    Tokens to take text are return tokens, i.e., characters, words, etc.

    Parameters
    ----------
    token_type : "char", "word", or "pattern"
        The type of tokens we will generated. If "char", the Tokens will return
        characters. If "word", the Tokens will return words. If "pattern", the
        Tokens will use the `token_pattern` parameter to match tokens. (Default: "pattern").
    token_pattern : str
        The regular expression used to match tokens. If `token_type` is "char", this
        parameter is ignored and the pattern will be set to `r"."`. If `token_type` is
        "word", this parameter is ignored and the pattern will be set to
        `r"(?u)\b\w\w+\b"`. (Default: r"(?u)\b\w\w+\b").
    copy : bool
        If True, the Tokens will return a copy of the tokens. If False, the Tokens
        will yield the tokens. (Default: True).
    """

    def __init__(self, token_type="pattern", token_pattern=r"(?u)\b\w\w+\b", copy=True):
        r"""
        Create a Tokens.

        Parameters
        ----------
        token_type : "char", "word", or "pattern"
            The type of tokens we will generated. If "char", the Tokens will return
            characters. If "word", the Tokens will return words. If "pattern", the
            Tokens will use the `token_pattern` parameter to match tokens. (Default: "pattern").
        token_pattern : str
            The regular expression used to match tokens. If `token_type` is "char", this
            parameter is ignored and the pattern will be set to `r"."`. If `token_type` is
            "word", this parameter is ignored and the pattern will be set to
            `r"(?u)\b\w\w+\b"`. (Default: r"(?u)\b\w\w+\b").
        copy : bool
            If True, the Tokens will return a copy of the tokens. If False, the Tokens
            will yield the tokens. (Default: True).

        Returns
        -------
        self : object
            A Tokens object that can be used to tokenize documents.
        """

        if "char" in token_type.lower():
            token_pattern = r"."
        elif "word" in token_type.lower():
            token_pattern = r"(?u)\b\w\w+\b"
        self.token_pattern = token_pattern
        self.tokenizer = re.compile(token_pattern).findall
        self.copy = copy

    def fit(self, documents=None, y=None):
        """
        Fit method. This is here for compatibility, but this does not explicitly do
        anything.

        Parameters
        ----------
        documents : None
            This parameter is ignored.
        y : None
            This parameter is ignored.

        Returns
        -------
        self : object
            Fitted Tokens model. This is the same as the input object.
        """

        return self

    def transform(self, documents):
        """
        Transform `documents` into a list of tokens.

        Parameters
        ----------
        documents : iterable
            An iterable of str.

        Returns
        -------
        tokens : iterable
            An iterable of tokens. If `copy` is True, this will be a list of tokens.
            If `copy` is False, this will be a generator that yields tokens.
        """

        tokens = (tuple(self.tokenizer(item)) for item in documents)

        if self.copy:
            return list(tokens)

        return tokens

    def fit_transform(self, documents, y=None):
        """
        Fit Tokens and then transform

        Parameters
        ----------
        documents : iterable
            An iterable of str.
        y : None
            This parameter is ignored.

        Returns
        -------
        tokens : list
        """

        documents1, documents2 = tee(documents) if not self.copy else (documents, documents)
        self.fit(documents1)
        return self.transform(documents2)


class Kmers:
    """
    Create Kmers.

    Parameters
    ----------
    k : :obj:`int` or :obj:`tuple` of :obj:`int`
        Size of k-mer. If :obj:`int`, only k-mers of that size will be returned. If a
        :obj:`tuple`, there must be two values with the minimum and maximize k-mer
        sizes.
    copy : bool
        If True, the k-merizer will return a copy of the k-mers. If False, the k-merizer
        will yield the k-mers. (Default: True).
    """

    def __init__(self, k, case=None, copy=True):
        """
        Create Kmers.

        Parameters
        ----------
        k : :obj:`int` or :obj:`tuple` of :obj:`int`
            Size of k-mer. If :obj:`int`, only k-mers of that size will be returned. If a
            :obj:`tuple`, there must be two values with the minimum and maximize k-mer
            sizes.
        copy : bool
            If True, the k-merizer will return a copy of the k-mers. If False, the k-merizer
            will yield the k-mers. (Default: True).

        Returns
        -------
        self : object
            A Kmers object that can be used to generate k-mers from tokens.
        """

        if isinstance(k, int):
            k = (k, k)

        self.k = k
        self.copy = copy
        self.vocabulary = None

    def _generate_kmers(self, item):
        """
        Generate k-mers from a single item.

        Parameters
        ----------
        item : str
            The input string from which to generate k-mers.

        Returns
        -------
        kmers : tuple
            A tuple of k-mers generated from the input string.
        """

        kmers = []
        for k in range(self.k[0], self.k[1] + 1):
            for i in range(len(item) - k + 1):
                kmer = tuple(item[i : i + k])
                if self.vocabulary is None or kmer in self.vocabulary:
                    kmers.append(kmer)

        return list(kmers)

    def fit(self, tokens, y=None):
        """
        Fit Kmers model given `tokens`. Fitting establishes the vocabulary of tokens.

        Parameters
        ----------
        tokens : iterable
            An iterable of str.
        y : None
            This parameter is ignored.

        Returns
        -------
        self : object
            Fitted Kmers model.
        """

        self.vocabulary = None
        vocabulary = set()
        for item in iter(tokens):
            vocabulary |= set(self._generate_kmers(item))
        self.vocabulary = vocabulary

        return self

    def fit_transform(self, tokens, y=None):
        """
        Parameters
        ----------
        tokens : iterable
            An iterable which generates either str, unicode or file objects.

        Returns
        -------
        kmers : list of lists
            Kmers generated from the input tokens. Each list contains k-mers for a
            single input item.
        """

        tokens1, tokens2 = tee(tokens) if not self.copy else (tokens, tokens)
        self.fit(tokens1)
        return self.transform(tokens2)

    def transform(self, tokens):
        """
        Apply Kmers model to `tokens`.

        Parameters
        ----------
        tokens : iterable
            An iterable which generates either str, unicode or file objects.

        Returns
        -------
        kmers : list of lists
            Kmers generated from the input tokens. Each list contains k-mers for a
            single input item.
        """

        kmers = (self._generate_kmers(item) for item in iter(tokens))

        if self.copy:
            return list(kmers)

        return kmers


class Bag:
    """
    Bag of Words (Bag) model.
    """

    def __init__(self):
        """
        Create a Bag model.
        """

        self.vocabulary = None

    def fit(self, kmers, y=None):
        """
        Fit Bag model given `kmers`. This establishes the vocabulary of k-mers.

        Parameters
        ----------
        kmers : iterable
            An iterable of k-mers, where each k-mer is a list or tuple of characters.
        y : None
            This parameter is ignored.

        Returns
        -------
        self : object
            Fitted Bag model.
        """

        self.vocabulary = None
        vocabulary = set()
        for item in iter(kmers):
            vocabulary |= set(item)
        self.vocabulary = sorted(vocabulary)

        return self

    def fit_transform(self, kmers, y=None):
        """
        Fit Bag model and then transform `kmers`.

        Parameters
        ----------
        kmers : iterable
            An iterable of k-mers, where each k-mer is a list or tuple of characters.
        y : None
            This parameter is ignored.

        Returns
        -------
        Bag : matrix of shape (n_samples, n_features)
            Bag of Words representation of the input k-mers. Each row corresponds to an
            input item, and each column corresponds to a k-mer in the vocabulary.
        """

        self.fit(kmers)
        return self.transform(kmers)

    def transform(self, kmers):
        """
        Apply Bag model to `kmers`.

        Parameters
        ----------
        kmers : iterable
            An iterable of k-mers, where each k-mer is a list or tuple of characters.

        Returns
        -------
        Bag : matrix of shape (n_samples, n_features)
            Bag of Words representation of the input k-mers. Each row corresponds to an
            input item, and each column corresponds to a k-mer in the vocabulary.
        """

        vocabulary_index = {kmer: i for i, kmer in enumerate(self.vocabulary)}
        print(vocabulary_index)
        bag = []
        for i, item in enumerate(iter(kmers)):
            bag.append(np.zeros(len(self.vocabulary), dtype=int))
            for kmer in item:
                if kmer in self.vocabulary:
                    bag[-1][vocabulary_index[kmer]] += 1
        print(bag)
        return np.array(bag, dtype=int)

