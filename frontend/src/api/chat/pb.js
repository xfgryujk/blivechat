import protobuf, { Field, Root, Type } from 'protobufjs'

const Long = protobuf.util.Long

export function longToNumber(value) {
  return Long && value instanceof Long ? value.toNumber() : value
}

const SendGiftV2MedalInfo = new Type('SendGiftV2MedalInfo')
  .add(new Field('target_id', 1, 'int64'))
  .add(new Field('medal_level', 5, 'int64'))
  .add(new Field('medal_name', 6, 'string'))

const SendGiftV2GiftMaterialSnapShot = new Type('SendGiftV2GiftMaterialSnapShot')
  .add(new Field('img_basic', 1, 'string'))

const SendGiftV2GiftItem = new Type('SendGiftV2GiftItem')
  .add(new Field('gift_id', 1, 'int64'))
  .add(new Field('gift_name', 2, 'string'))
  .add(new Field('num', 3, 'int64'))
  .add(new Field('total_coin', 7, 'int64'))
  .add(new Field('coin_type', 8, 'string'))
  .add(new Field('timestamp', 10, 'int64'))
  .add(new Field('gift_info', 35, 'SendGiftV2GiftMaterialSnapShot'))

export const SendGiftBroadcast = new Type('SendGiftBroadcast')
  .add(new Field('uid', 1, 'int64'))
  .add(new Field('uname', 2, 'string'))
  .add(new Field('face', 3, 'string'))
  .add(new Field('guard_level', 5, 'int64'))
  .add(new Field('medal_info', 8, 'SendGiftV2MedalInfo'))
  .add(new Field('gift_list', 10, 'SendGiftV2GiftItem', 'repeated'))

export const root = new Root()
  .define('bilibili.live.gift.v1')
  .add(SendGiftV2MedalInfo)
  .add(SendGiftV2GiftMaterialSnapShot)
  .add(SendGiftV2GiftItem)
  .add(SendGiftBroadcast)
