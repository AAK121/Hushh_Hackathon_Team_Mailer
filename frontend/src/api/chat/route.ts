import { openai } from '@ai-sdk/openai';
import {
  createUIMessageStreamResponse,
  createUIMessageStream,
  streamText,
  convertToModelMessages,
  stepCountIs,
} from 'ai';
import { processToolCalls } from '../../lib/utils';
import { tools } from '../../lib/tools';
import { HumanInTheLoopUIMessage } from '../../lib/types';

// Allow streaming responses up to 30 seconds
export const maxDuration = 30;

export async function POST(req: Request) {
  try {
    const { messages }: { messages: HumanInTheLoopUIMessage[] } =
      await req.json();

    const stream = createUIMessageStream({
      execute: async ({ writer }) => {
        // Utility function to handle tools that require human confirmation
        // Checks for confirmation in last message and then runs associated tool
        const processedMessages = await processToolCalls(
          {
            messages,
            writer,
            tools,
          },
          {
            // type-safe object for tools without an execute function
            getWeatherInformation: async ({ city }) => {
              const conditions = ['sunny', 'cloudy', 'rainy', 'snowy'];
              return `The weather in ${city} is ${
                conditions[Math.floor(Math.random() * conditions.length)]
              }.`;
            },
            sendEmail: async ({ to, subject, body }) => {
              // Simulate sending email
              console.log('Sending email:', { to, subject, body });
              return `Email sent successfully to ${to} with subject "${subject}"`;
            },
            scheduleCalendarEvent: async ({ title, date, time, duration }) => {
              // Simulate scheduling calendar event
              console.log('Scheduling event:', { title, date, time, duration });
              return `Calendar event "${title}" scheduled for ${date} at ${time}${duration ? ` (Duration: ${duration})` : ''}`;
            },
          },
        );

        const result = streamText({
          model: openai('gpt-4o'),
          messages: convertToModelMessages(processedMessages),
          tools,
          stopWhen: stepCountIs(5),
        });

        writer.merge(
          result.toUIMessageStream({ originalMessages: processedMessages }),
        );
      },
    });

    return createUIMessageStreamResponse({ stream });
  } catch (error) {
    console.error('Chat API Error:', error);
    return new Response('Internal Server Error', { status: 500 });
  }
}
