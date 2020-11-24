const express = require('express');
var router = express.Router();
var ctrlHome = require('../controller/homeController');

router.get('/', ctrlHome.home);

module.exports = router;