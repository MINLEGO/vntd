# Vinted client

A Python client that exposes Vinted listings and their sellers through models shaped like those of the sibling Leboncoin client, so that an attribute with the same name means the same thing in both.

## Language

**Ad**:
A listing for one item put on sale by a seller on Vinted.
_Avoid_: Item, product, article

**Seller**:
The person who puts an Ad on sale.
_Avoid_: User, owner, member

**Status**:
Where an Ad stands in its life as a listing (active, reserved or sold). Says nothing about the physical state of the item.
_Avoid_: State, condition

**Condition**:
The physical state of the item being sold (for example new with tag, very good).
_Avoid_: Status, state
