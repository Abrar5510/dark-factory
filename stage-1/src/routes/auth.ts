import { Router } from 'express';
import { userRepository } from '../repositories/userRepository';
import { Utils } from '../utils';
import { errors } from '../middleware/errorHandler';

const router = Router();

// POST /auth/signup
router.post('/signup', async (req, res, next) => {
  try {
    const { email, password, display_name } = req.body;

    // Validate required fields
    if (!email || !password || !display_name) {
      throw errors.validationFailed('Missing required fields: email, password, display_name');
    }

    // Create user
    const user = await userRepository.create(email, password, display_name);
    
    // Create session token
    const token = userRepository.createSession(user.id);

    res.status(201).json({
      user_id: user.id,
      display_name: user.display_name,
      token: token
    });
  } catch (error) {
    next(error);
  }
});

// POST /auth/login
router.post('/login', async (req, res, next) => {
  try {
    const { email, password } = req.body;

    // Validate required fields
    if (!email || !password) {
      throw errors.validationFailed('Missing required fields: email, password');
    }

    // Authenticate user
    const user = await userRepository.authenticate(email, password);
    if (!user) {
      throw errors.unauthenticated();
    }

    // Create new session token
    const token = userRepository.createSession(user.id);

    res.status(200).json({
      user_id: user.id,
      display_name: user.display_name,
      token: token
    });
  } catch (error) {
    next(error);
  }
});

export { router as authRoutes };