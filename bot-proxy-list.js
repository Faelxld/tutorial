const request = require('request')
const cheerio = require('cheerio')
const fs = require('fs')
const util = require('util')
const promisify = util.promisify

const readFile = promisify(fs.readFile)
const existFile = promisify(fs.exists)
const writeFile = promisify(fs.writeFile)
const get = promisify(request)

const log = async (text) => {
    await appendFile(loja + '.log', new Date().toLocaleString() + ' - ' + text + '\n')
}

const proxyFile = 'proxys.json'

var url = 'http://meuip.com/api/meuip.php'

function ValidateIPaddress(ipaddress) {  
    if (/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(ipaddress)) {  
        return true
    }  
    return false
}  

var start = async () => {
    // var response = {
    //     body: await readFile('megaproxylist.html'),
    //     statusCode: 200
    // }
    
    try {
        var response = await get('http://www.megaproxylist.net/')
    }
    catch (e) {
        throw new Error("Erro ao buscar dados do megaproxylist.net")
    }
    
    if (response.statusCode !== 200)
        throw new Error("Erro ao realizar requisição para buscar os proxys")
    
    var proxys = []

    if (await existFile(proxyFile)) {
        var contentProxyFile = await readFile(proxyFile)
        contentProxyFile = JSON.parse(contentProxyFile)
        
        for (var i = 0; i < contentProxyFile.length; i++) {
            
            try {
                var proxy = 'http://' + contentProxyFile[i].proxy.replace('http://', '')
                console.log("tentando proxy " + proxy);
                var reqOpts = {
                    url: url, 
                    method: "GET", 
                    headers: {"Cache-Control" : "no-cache"}, 
                    proxy: proxy,
                    timeout: 3000};
                
                var r = await get(reqOpts)
                
                if (r.statusCode !== 200 || !ValidateIPaddress(r.body))
                    continue
                
                proxys.push({
                    proxy: proxy,
                    speed: contentProxyFile[i].speed,
                    ip: r.body.trim()
                })
            }
            catch (e) {
                //console.log(e)
            }
        }
    }
    
    const $ = cheerio.load(response.body)

    var elements = $('table.myTableProxy tr:not(.myTableProxy)')
    
    for (var i = 1; i < elements.length; i++) {
        try {
            var proxy = 'http://' + $(elements[i]).find('td:nth-child(1)').text().trim()
            console.log("tentando proxy " + proxy);
            var speed = parseInt($(elements[i]).find('td:nth-child(4)').text().trim())
            var reqOpts = {
                url: url, 
                method: "GET", 
                headers: {"Cache-Control" : "no-cache"}, 
                proxy: proxy,
                timeout: 3000};

            var r = await get(reqOpts)
            
            if (r.statusCode !== 200 || !ValidateIPaddress(r.body))
                continue
            
            var exist = proxys.filter((p) => {
                return p.proxy === proxy;
            })[0]

            if ((exist && exist.speed > speed) || !exist) {
                proxys.push({
                    proxy: proxy,
                    speed: speed,
                    ip: r.body.trim()
                })      
            }    
        }
        catch (e) {
            //console.log(e)
        }
    }

    //elimina os repetidos
    proxys = proxys.filter(function(item, pos) {
        return proxys.indexOf(item) == pos;
    })
    console.log('escrevendo no arquivo')
    await writeFile(proxyFile, JSON.stringify(proxys))
}

start()
