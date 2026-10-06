import { Router } from 'express';

const router = Router();

// TODO: Implement settlement endpoints
router.post('/', (req, res) => {
  res.status(501).json({ error: { code: 'not_implemented', message: 'Settlement endpoint not yet implemented' } });
});

export { router as settlementRoutes };