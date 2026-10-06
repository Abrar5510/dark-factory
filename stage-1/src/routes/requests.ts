import { Router } from 'express';

const router = Router();

// TODO: Implement request endpoints
router.post('/', (req, res) => {
  res.status(501).json({ error: { code: 'not_implemented', message: 'Request endpoint not yet implemented' } });
});

export { router as requestRoutes };