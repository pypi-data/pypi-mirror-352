from big_thing_py.utils.exception_util import *
from big_thing_py.utils.log_util import *
from big_thing_py.utils.json_util import *

from gmqtt import Message as MQTTMessage


def encode_MQTT_message(topic: str, payload: Union[str, dict]) -> MQTTMessage:
    try:
        if isinstance(payload, str):
            payload = bytes(payload, encoding='utf-8')
        elif isinstance(payload, dict):
            payload = dict_to_json_string(payload)

        return MQTTMessage(topic, payload)
    except Exception as e:
        print_error(e)
        raise e


def decode_MQTT_message(msg: MQTTMessage, mode=dict) -> Tuple[str, dict]:
    topic = msg.topic
    payload = msg.payload

    if isinstance(topic, bytes):
        topic = topic.decode()
    if isinstance(payload, bytes):
        payload = payload.decode()

    if isinstance(payload, str):
        if mode == str:
            return topic, payload
        elif mode == dict:
            return topic, json_string_to_dict(payload)
        else:
            raise MXNotSupportedError(f'Unexpected mode!!! - {mode}')
    elif isinstance(payload, dict):
        if mode == str:
            return topic, dict_to_json_string(payload)
        elif mode == dict:
            return topic, payload
        else:
            raise MXNotSupportedError(f'Unexpected mode!!! - {mode}')
    else:
        raise MXNotSupportedError(f'Unexpected type!!! - {type(payload)}')


def topic_split(topic: str):
    return topic.split('/')


def topic_join(topic: List[str]):
    return '/'.join(topic)


def unpack_mqtt_message(msg: MQTTMessage) -> Tuple[List[str], str]:
    topic, payload = decode_MQTT_message(msg, dict)
    topic = topic_split(topic)

    return topic, payload


def pack_mqtt_message(topic_list: List[str], payload: str) -> MQTTMessage:
    topic = topic_join(topic_list)
    msg = encode_MQTT_message(topic, payload)

    return msg


# ref from paho.mqtt.python: (https://github.com/eclipse-paho/paho.mqtt.python)
class MQTTMatcher:
    """Intended to manage topic filters including wildcards.

    Internally, MQTTMatcher use a prefix tree (trie) to store
    values associated with filters, and has an iter_match()
    method to iterate efficiently over all filters that match
    some topic name."""

    class Node:
        __slots__ = '_children', '_content'

        def __init__(self):
            self._children = {}
            self._content = None

    def __init__(self):
        self._root = self.Node()

    def __setitem__(self, key, value):
        """Add a topic filter :key to the prefix tree
        and associate it to :value"""
        node = self._root
        for sym in key.split('/'):
            node = node._children.setdefault(sym, self.Node())
        node._content = value

    def __getitem__(self, key):
        """Retrieve the value associated with some topic filter :key"""
        try:
            node = self._root
            for sym in key.split('/'):
                node = node._children[sym]
            if node._content is None:
                raise KeyError(key)
            return node._content
        except KeyError as ke:
            raise KeyError(key) from ke

    def __delitem__(self, key):
        """Delete the value associated with some topic filter :key"""
        lst = []
        try:
            parent, node = None, self._root
            for k in key.split('/'):
                parent, node = node, node._children[k]
                lst.append((parent, k, node))
            # TODO
            node._content = None
        except KeyError as ke:
            raise KeyError(key) from ke
        else:  # cleanup
            for parent, k, node in reversed(lst):
                if node._children or node._content is not None:
                    break
                del parent._children[k]

    def iter_match(self, topic):
        """Return an iterator on all values associated with filters
        that match the :topic"""
        lst = topic.split('/')
        normal = not topic.startswith('$')

        def rec(node, i=0):
            if i == len(lst):
                if node._content is not None:
                    yield node._content
            else:
                part = lst[i]
                if part in node._children:
                    for content in rec(node._children[part], i + 1):
                        yield content
                if '+' in node._children and (normal or i > 0):
                    for content in rec(node._children['+'], i + 1):
                        yield content
            if '#' in node._children and (normal or i > 0):
                content = node._children['#']._content
                if content is not None:
                    yield content

        return rec(self._root)
