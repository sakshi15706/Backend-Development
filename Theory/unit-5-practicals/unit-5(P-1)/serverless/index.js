'use strict';
/**
 * Task 3: serverless consumer for e-mail dispatch (Google Functions Framework entry point).
 *
 * STATELESS on purpose: no module-level cache, no database pool, no open connection. Each
 * call gets everything it needs from the request and the environment, so the platform can run
 * zero, one or a thousand copies. Anything that must be remembered (e.g. "was this event
 * already processed?") belongs in a database, which the caller (the bridge) handles.
 *
 * MAIL_API_URL unset  -> dry run: the e-mail is only logged (the slide's api.mail-mock.local host
 *                        does not exist, so calling it would always fail).
 */
const MAIL_TIMEOUT_MS = 5000;

exports.sendAttendanceEmail = async (req, res) => {
  const event = req.body;

  if (!event || event.type !== 'attendance.marked') return res.status(204).end();   // not for us
  if (!event.studentId || !event.eventId) {
    return res.status(400).json({ ok: false, error: 'studentId and eventId are required' });
  }

  const mail = {
    to: `${event.studentId}@sms.example`,
    subject: 'Attendance update',
    text: `Attendance for ${event.classId || 'your class'}: ${event.present ? 'present' : 'absent'}`,
  };

  const url = process.env.MAIL_API_URL;
  if (!url) {
    console.log(JSON.stringify({ severity: 'INFO', message: 'dry run: e-mail not sent', eventId: event.eventId, to: mail.to }));
    return res.status(200).json({ ok: true, dryRun: true, eventId: event.eventId });
  }

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(mail),
      signal: AbortSignal.timeout(MAIL_TIMEOUT_MS),      // never wait forever on a dependency
    });
    if (!response.ok) throw new Error(`mail API answered ${response.status}`);
  } catch (err) {
    console.error(JSON.stringify({ severity: 'ERROR', message: err.message, eventId: event.eventId }));
    return res.status(502).json({ ok: false, error: 'mail provider unavailable' });   // caller will retry
  }
  return res.status(200).json({ ok: true, eventId: event.eventId });
};
