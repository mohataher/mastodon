#!/usr/bin/env python
#
# Copyright 2012 8pen

"""A simple trie with some prediction functions"""

class Trie:

    @staticmethod
    def tokenize_unigram(line):
        """Tokenize a line unigrams, as generated by count.pl, into a pair of
        the form (weight, unigram)

        :param line: a line of the form "weight word"
        """
        stripped = line.strip()
        if not stripped:
            return
        
        s = stripped.split(' ')
        if len(s) < 2:
            return

        # tokens = list(s[1])
        # weight = s[0]
        return (s[0], list(s[1]))

    @staticmethod
    def tokenize_ngram(line):
        """Tokenize a line ngrams, as generated by count.pl, into a pair of
        the form (weight, [word1, word2, ...])

        :param line: a line of the form "word1<>word2<>...<>rank weight (other weights)"
        """
        stripped = line.strip()
        if not stripped:
            return
        
        s = stripped.split(' ')
        if len(s) < 2:
            return

        tokens = s[0].split('<>')
        # weight = s[1]
        return (s[1], [token for token in tokens[0:len(tokens)-1] if token])

    @staticmethod
    def from_files(filenames,is_ngram=False):
        """Construct a trie of unigrams or ngrams from a list of files,
        as generated by count.pl

        :param filenames: a list of filenames
        :param is_ngram: True if the files contain ngrams, unigrams otherwise
        """
        t = Trie()
        for filename in filenames:
            print "Tokenizing " + str(filename)
            f = open(filename, 'r')
            for line in f:
                try:
                    if is_ngram:
                        (weight, tokens) = Trie.tokenize_ngram(line) or (0, None)
                    else:
                        (weight, tokens) = Trie.tokenize_unigram(line) or (0, None)
                    if tokens:
                        t[tokens] = weight
                except:
                    continue
            f.close()
        return t

    def __init__(self):
        self.path = {}
        self.value = None
        self.value_valid = False

    def __setitem__(self, key, value):
        head = key[0]
        if head in self.path:
            node = self.path[head]
        else:
            node = Trie()
            self.path[head] = node

        if len(key) > 1:
            remains = key[1:]
            node.__setitem__(remains, value)
        else:
            node.value = value
            node.value_valid = True

    def __delitem__(self, key):
        head = key[0]
        if head in self.path:
            node = self.path[head]
            if len(key) > 1:
                remains = key[1:]
                node.__delitem__(remains)
            else:
                node.value_valid = False
                node.value = None
            if len(node) == 0:
                del self.path[head]

    def __getitem__(self, key):
        head = key[0]
        if head in self.path:
            node = self.path[head]
        else:
            raise KeyError(key)
        if len(key) > 1:
            remains = key[1:]
            try:
                return node.__getitem__(remains)
            except KeyError:
                raise KeyError(key)
        elif node.value_valid:
            return node.value
        else:
            raise KeyError(key)

    def __contains__(self, key):
        try:
            self.__getitem__(key)
        except KeyError:
            return False
        return True

    # Number of children nodes
    def __len__(self):
        n = 1 if self.value_valid else 0
        for k in self.path.iterkeys():
            n = n + len(self.path[k])
        return n

    def keys(self, prefix=[]):
            result = []
            if self.value_valid:
                isStr = True
                val = ""
                for k in prefix:
                    if type(k) != str or len(k) > 2:
                        isStr = False
                        break
                    else:
                        val += k
                if isStr:
                    result.append(val)
                else:
                    result.append(prefix)
            for k in self.path.iterkeys():
                next = []
                next.extend(prefix)
                next.append(k)
                result.extend(self.path[k].keys(next))
            return result

    def get_next(self, prefix):
        head = prefix[0]
        if head in self.path:
            node = self.path[head]
        else:
            raise KeyError(prefix)
            
        if len(prefix) > 1:
            remains = prefix[1:]
            try:
                #return node.get_prefix(remains)
                return node.get_next(remains)
            except KeyError:
                raise KeyError(prefix)
        else:
            return node

    def get_predictions(self, tokens, num_candidates=5):
        import operator
        try:
            return sorted(self.get_next(tokens).path.items(),
                key=lambda c: c[1], reverse=True)
        except KeyError:
            return []

    def dump(self):
        print "Dumping trie:"
        for k in self.keys():
            print "  t[%s] = %s" % (k, self[k])