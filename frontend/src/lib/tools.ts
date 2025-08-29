import { tool, ToolSet } from 'ai';
import { z } from 'zod';
import { hushMCPAgentAPI } from '../services/hushMCPAgentAPI';

const getWeatherInformation = tool({
  description: 'show the weather in a given city to the user',
  inputSchema: z.object({ city: z.string() }),
  outputSchema: z.string(),
  // no execute function, we want human in the loop
});

const getLocalTime = tool({
  description: 'get the local time for a specified location',
  inputSchema: z.object({ location: z.string() }),
  outputSchema: z.string(),
  // including execute function -> no confirmation required
  execute: async ({ location }: { location: string }) => {
    console.log(`Getting local time for ${location}`);
    return new Date().toLocaleTimeString('en-US', {
      timeZone: 'UTC',
      hour12: true,
      hour: 'numeric',
      minute: '2-digit'
    }) + ` (${location})`;
  },
});

const sendEmail = tool({
  description: 'send an email to specified recipients',
  inputSchema: z.object({ 
    to: z.string(),
    subject: z.string(),
    body: z.string()
  }),
  outputSchema: z.string(),
  // no execute function, requires human approval
});

const scheduleCalendarEvent = tool({
  description: 'schedule a calendar event using HushMCP AddToCalendar agent',
  inputSchema: z.object({
    title: z.string(),
    date: z.string(),
    time: z.string(),
    duration: z.string().optional(),
    description: z.string().optional(),
    location: z.string().optional()
  }),
  outputSchema: z.string(),
  // no execute function, requires human approval for HushMCP integration
});

const createEmailCampaign = tool({
  description: 'create and manage email marketing campaigns using HushMCP MailerPanda agent',
  inputSchema: z.object({
    campaignDescription: z.string(),
    targetAudience: z.string(),
    sender: z.string(),
    recipients: z.array(z.string()).optional()
  }),
  outputSchema: z.string(),
  // no execute function, requires human approval
});

export const tools = {
  getWeatherInformation,
  getLocalTime,
  sendEmail,
  scheduleCalendarEvent,
  createEmailCampaign,
} satisfies ToolSet;
