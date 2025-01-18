class Crypto {
    constructor() {
        this.go = new Go();
    }

    load() {
        var go = this.go
        let promise = new Promise(function(ok, err) {
            WebAssembly.instantiateStreaming(fetch("/src/crypto/cryptolib.wasm"), go.importObject).then((result) => {
                go.run(result.instance);
                ok()
            })
        })
        return promise
    }

    prvkey() {
        return __cryptolib__prvkey()
    }

    id(prvkey) {
        return __cryptolib__id(prvkey)
    }

    sign(msg, prvkey) {
        return __cryptolib__sign(msg, prvkey)
    }

    hash(msg) {
        return __cryptolib__hash(msg)
    }

    recoverid(msg, sig) {
        return __cryptolib__recoverid(msg, sig)
    }

}
