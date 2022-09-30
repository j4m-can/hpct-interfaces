#! /usr/bin/env python3

import json
import time

COUNT = 500000


def encode(v: bool) -> str:
    if v == True:
        return "1"
    if v == False:
        return "0"
    raise Exception()


def decode(v: str) -> bool:
    if v == "1":
        return True
    if v == "0":
        return False
    raise Exception()


def bmencode(v: bool) -> str:
    match v:
        case True:
            return "1"
        case False:
            return "0"
    raise Exception()


def bmdecode(v: str) -> bool:
    match v:
        case "1":
            return True
        case "0":
            return False
    raise Exception()


def bencode(v: bool) -> str:
    if v in [True, False]:
        return v and "1" or "0"
    raise Exception()


def bdecode(v: str) -> bool:
    if v in ["0", "1"]:
        return v == "1"
    raise Exception


BOOL_VALUES = [True, False]
ENCODED_BOOL_VALUES = ["0", "1"]


def bbencode(v: bool) -> str:
    if v in BOOL_VALUES:
        return v and "1" or "0"
    raise Exception()


def bbdecode(v: str) -> bool:
    if v in ENCODED_BOOL_VALUES:
        return v == "1"
    raise Exception


t0 = time.time()
for i in range(COUNT):
    v = json.loads(json.dumps(True))
t1 = time.time()
print(f"json elapsed ({t1-t0})")

t0 = time.time()
for i in range(COUNT):
    v = decode(encode(True))
t1 = time.time()
print(f"if elapsed ({t1-t0})")

t0 = time.time()
for i in range(COUNT):
    v = bmdecode(bmencode(True))
t1 = time.time()
print(f"match elapsed ({t1-t0})")

t0 = time.time()
for i in range(COUNT):
    v = bdecode(bencode(True))
t1 = time.time()
print(f"list elapsed ({t1-t0})")

t0 = time.time()
for i in range(COUNT):
    v = bbdecode(bbencode(True))
t1 = time.time()
print(f"predef list elapsed ({t1-t0})")
