export class Trie {
  constructor() {
    this._root = this._createNode()
  }

  _createNode() {
    return {
      children: {}, // char -> node
      value: null
    }
  }

  set(key, value) {
    if (key === '') {
      throw new Error('key is empty')
    }
    let node = this._root
    for (let char of key) {
      let nextNode = node.children[char]
      if (nextNode === undefined) {
        nextNode = node.children[char] = this._createNode()
      }
      node = nextNode
    }
    node.value = value
  }

  get(key) {
    let node = this._root
    for (let char of key) {
      let nextNode = node.children[char]
      if (nextNode === undefined) {
        return null
      }
      node = nextNode
    }
    return node.value
  }

  has(key) {
    return this.get(key) !== null
  }

  lazyMatch(str) {
    let node = this._root
    for (let char of str) {
      let nextNode = node.children[char]
      if (nextNode === undefined) {
        return null
      }
      if (nextNode.value !== null) {
        return nextNode.value
      }
      node = nextNode
    }
    return null
  }
}
