const input = 0
const output = 1
const err = 2
const env = 3
const Waiting = 0;
const Running = 1;
const Success = 2;
const Failed = 3;

class Colonies {
    constructor(host, port) {
        this.crypto = new Crypto()
        this.host = host
        this.port = port
    }

    load() {
        var crypto = this.crypto
        let promise = new Promise(function(ok, err) {
            crypto.load().then(() => {
                ok()
            })
        })
        return promise
    }

    crypto() {
        return this.crypto
    }

    sendRPCMsg(msg, prvkey) {
        let rpcMsg = {
            "payloadtype": msg.msgtype,
            "payload": "",
            "signature": ""
        }

        rpcMsg.payload = btoa(JSON.stringify(msg))
        rpcMsg.signature = this.crypto.sign(rpcMsg.payload, prvkey)

        var host = this.host
        var port = this.port

        let promise = new Promise(function(resolve, reject) {
            try {
                $.ajax({
                    type: "POST",
                    url: "http://" + host + ":" + port + "/api",
                    data: JSON.stringify(rpcMsg),
                    contentType: 'plain/text',
                    success: function(response) {
                        let rpcReplyMsg = JSON.parse(response)
                        let msg = JSON.parse(atob(JSON.parse(response).payload))
                        if (rpcReplyMsg.error == true) {
                            reject(msg)
                        } else {
                            resolve(msg)
                        }
                    },
                    error: function(xhr, status, error) {
                        reject(error)
                    }
                })
            } catch (e) {
                reject(e)
            }
        })
        return promise
    }

    addColony(colony, prvkey) {
        var msg = {
            "msgtype": "addcolonymsg",
            "colony": colony
        }

        return this.sendRPCMsg(msg, prvkey)
    }

    getColonies(prvkey) {
        var msg = {
            "msgtype": "getcoloniesmsg"
        }

        return this.sendRPCMsg(msg, prvkey)
    }

    getColony(colonyID, prvkey) {
        var msg = {
            "msgtype": "getcolonymsg",
            "colonyid": colonyId
        }

        return this.sendRPCMsg(msg, prvkey)
    }

    addExecutor(executor, prvkey) {
        var msg = {
            "msgtype": "addexecutormsg",
            "executor": executor
        }

        return this.sendRPCMsg(msg, prvkey)
    }

    rejectExecutor(executorId, prvkey) {
        var msg = {
            "msgtype": "rejectexecutormsg",
            "executorid": executorId
        }

        return this.sendRPMsg(msg, prvkey)
    }

    approveExecutor(executorId, prvkey) {
        var msg = {
            "msgtype": "approveexecutormsg",
            "executorid": executorId
        }

        return this.sendRPCMsg(msg, prvkey)
    }

    submit(spec, prvkey) {
        var msg = {
            "msgtype": "submitfuncspecmsg",
            "spec": spec
        }

        return this.sendRPCMsg(msg, prvkey)
    }

    getProcess(processId, prvkey) {
        var msg = {
            "msgtype": "getprocessmsg",
            "processid": processId
        }

        return this.sendRPCMsg(msg, prvkey)
    }


    getProcesses(colonyId, count, state, prvkey) {
        var msg = {
            "msgtype": "getprocessesmsg",
            "colonyid": colonyId,
            "count": count,
            "state": state
        }

        return this.sendRPCMsg(msg, prvkey)
    }

    assign(colonyId, timeout, prvkey) {
        var msg = {
            "msgtype": "assignprocessmsg",
            "latest": false,
            "timeout": timeout,
            "colonyid": colonyId
        }

        return this.sendRPCMsg(msg, prvkey)
    }

    assignLatest(colonyId, timeout, prvkey) {
        var msg = {
            "msgtype": "assignprocessmsg",
            "latest": true,
            "timeout": timeout,
            "colonyid": colonyId
        }

        return this.sendRPCMsg(msg, prvkey)
    }

    addAttribute(attribute, prvkey) {
        attribute.attributetype = output

        var msg = {
            "msgtype": "addattributemsg",
            "attribute": attribute
        }

        return this.sendRPCMsg(msg, prvkey)
    }

    close(processId, prvkey) {
        var msg = {
            "msgtype": "closesuccessfulmsg",
            "processid": processId
        }

        return this.sendRPCMsg(msg, prvkey)
    }

    fail(processId, prvkey) {
        var msg = {
            "msgtype": "closefailedmsg",
            "processid": processId
        }

        return this.sendRPCMsg(msg, prvkey)
    }


    subscribeProcesses(executorType, timeout, state, prvkey, callback) {
        var msg = {
            "msgtype": "subscribeprocessesmsg",
            "executortype": executorType,
            "state": state,
            "timeout": timeout
        }

        let rpcMsg = {
            "payloadtype": msg.msgtype,
            "payload": "",
            "signature": ""
        }

        rpcMsg.payload = btoa(JSON.stringify(msg))
        rpcMsg.signature = this.crypto.sign(rpcMsg.payload, prvkey)

        let socket = new WebSocket("ws://" + this.host + ":" + this.port + "/pubsub");

        socket.addEventListener('open', function(event) {
            socket.send(JSON.stringify(rpcMsg));
        });

        let promise = new Promise(function(resolve, reject) {
            socket.addEventListener('close', function(event) {
                socket = null
                reject()
            });

            socket.addEventListener('error', function(event) {
                socket = null
                reject()
            });

            socket.addEventListener('message', function(event) {
                msg = JSON.parse(atob(JSON.parse(event.data).payload))
                callback(msg)
            });
        })
        return promise
    }
}
