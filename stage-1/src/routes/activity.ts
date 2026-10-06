import { Router } from 'express';

const router = Router();

// TODO: Implement activity endpoints
router.get('/', (req, res) => {
  res.status(501).json({ error: { code: 'not_implemented', message: 'Activity endpoint not yet implemented' } });
});

export { router as activityRoutes };