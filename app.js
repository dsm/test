var expressSession = require('express-session'),
    initPassport = require('./app_server/passport/init');
const express = require('express'),
    http1_port = 80,
    path = require('path'),
    bodyParser = require('body-parser'),
    cookieParser = require('cookie-parser'),
    app = express(),
    db = require('./app_server/models/db'),
    rfid = require('./app_server/rfid/rfid'),
    routerManager = require('./app_server/routes/routerManager'),
    flash = require('connect-flash'),
    passport = require('passport'),
    ejsLayout = require('express-ejs-layouts');

app.set('view engine', 'ejs')
app.set('views', path.join(__dirname, '/app_server/views'))
app.use(ejsLayout)

app.use(bodyParser.json())
app.use(bodyParser.urlencoded({ extended: 'false' }))
app.use(cookieParser())

app.use('/public', express.static(path.join(__dirname, 'public')))

app.use(expressSession({
    secret: 'mySecretKey',
    resave: false,
    saveUninitialized: true,
}))

app.use(passport.initialize())
app.use(passport.session())
app.use(flash())


initPassport(passport)

routerManager(app)

app.listen(http1_port, () => {
    console.log('Listening http server on port: ' + http1_port)
});