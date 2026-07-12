'use strict';

const express = require('express');
const router  = express.Router();
const userStore = require('../store/userStore');

// Dev-only debug route to list in-memory users (DO NOT enable in production)
if (process.env.NODE_ENV !== 'production') {
	router.get('/debug/users', async (req, res) => {
		try {
			const store = require('../store/userStore');
			if (store && typeof store._debugAll === 'function') {
				return res.json({ users: store._debugAll() });
			}
			// Fallback: read accounts.json
			const fs = require('fs');
			const p = require('path').join(__dirname, '../data/accounts.json');
			if (fs.existsSync(p)) {
				return res.json({ users: JSON.parse(fs.readFileSync(p, 'utf8') || '[]') });
			}
			return res.json({ users: [] });
		} catch (e) {
			return res.status(500).json({ error: 'debug unavailable', detail: e.message });
		}
	});
}

router.get('/', (req, res) => res.redirect('/login'));

module.exports = router;
