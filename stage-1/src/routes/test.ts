import { Router } from 'express';

const router = Router();

// POST /_test/reset
router.post('/reset', (req, res) => {
  res.status(501).json({ error: { code: 'not_implemented', message: 'Test reset endpoint not yet implemented' } });
});

// GET /_test/export
router.get('/export', (req, res) => {
  res.status(501).json({ error: { code: 'not_implemented', message: 'Test export endpoint not yet implemented' } });
});

// POST /_test/import
router.post('/import', (req, res) => {
  res.status(501).json({ error: { code: 'not_implemented', message: 'Test import endpoint not yet implemented' } });
});

export { router as testRoutes };