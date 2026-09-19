-- Filled from the SPEC at kickoff. Two rules the shape must keep:
--   * every amount is an INTEGER in the smallest indivisible unit, never a
--     float, so arithmetic is exact and rounding is a parse-time concern;
--   * every state-changing request records its own effect, so a replay can be
--     recognised and answered from the record instead of repeated.
PRAGMA user_version = 0;
