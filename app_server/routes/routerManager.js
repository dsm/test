var routeHome = require('./homeRouter');
var routeLogin = require('./loginRouter');
var routeLogout = require('./logoutRouter');
var routeSignup = require('./signupRouter');
var routeUsers = require('./usersRouter');
var routeHistory = require('./historyRouter');
var Users = require('../models/users').User

var isAuthenticated = (req, res, next) => {
    if (req.isAuthenticated()) {
        return next();
    }
    else {
        res.redirect('/login');
    }
};

var isAdmin = (req,res,next) =>{
    Users
        .findOne({username:req.user.username})
        .then((user) => {
            if(user.admin== true){
                next();
            }else{
                res.redirect('/');
            }
        })
        .catch(err => {
            console.log(err)
        });
}

module.exports = (app) => {
    app.use('/', routeHome);
    app.use('/home', routeHome);
    app.use('/login', routeLogin);
    app.use('/logout', isAuthenticated, routeLogout);
    app.use('/users', isAuthenticated, isAdmin,routeUsers);
    app.use('/history', isAuthenticated,isAdmin, routeHistory);
    app.use('/signup', isAuthenticated, isAdmin,routeSignup);
    app.use('/users/deleteUser', isAuthenticated,isAdmin, routeUsers);
    app.use('/users/updateUser', isAuthenticated,isAdmin, routeUsers);
    app.use('/users/addAdmin', isAuthenticated,isAdmin, routeUsers);
    app.use('/users/removeAdmin', isAuthenticated,isAdmin, routeUsers);
    app.use('/history/deleteUser', isAuthenticated,isAdmin, routeHistory);
};