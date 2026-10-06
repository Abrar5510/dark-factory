import { Router } from 'express';

const router = Router();

// TODO: Implement split endpoints
router.post('/', (req, res) => {
  res.status(501).json({ error: { code: 'not_implemented', message: 'Split endpoint not yet implemented' } });
});

export { router as splitRoutes };