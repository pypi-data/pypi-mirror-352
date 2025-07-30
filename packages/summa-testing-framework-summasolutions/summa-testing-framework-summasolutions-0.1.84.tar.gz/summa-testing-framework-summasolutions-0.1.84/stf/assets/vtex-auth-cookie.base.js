const _account = 'accountName',

      _payload = {
        appkey: 'appkey',
        apptoken: 'IFJSAKMGKXBCJOVNMISPNSQQAKJAIOLLNNQOOUPPCZYNFSIGIFVXZOXPOTRPBMYWMQOWXGYRTCMOUCKICDRCSOLZQBZVCZOQABBPDMIBHEDXBIVLIJNYUVEXEPFWHDOT',
      },

      _options = {
        method: 'POST',
        body: JSON.stringify(_payload),
        headers: { 'Content-Type': 'application/json' },
      }

// Execute
fetch( `https://${_account}.myvtex.com/api/vtexid/apptoken/login?an=${_account}`, _options )
  .then( (res) => res.json() )
  .then( (res) => document.cookie = 'VtexIdclientAutCookie='+ res.token +'; path=/;')
