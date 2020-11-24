module.exports.home = (req, res, next) => {
    if (!req.isAuthenticated()) {
        res.redirect('/login')
    } else {
        res.render('home',
            {
                admin: req.user.admin,
                userAuth: req.isAuthenticated(),
            });
        next();
    }

};