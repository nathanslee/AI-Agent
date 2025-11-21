import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const code = searchParams.get('code');
  const state = searchParams.get('state');
  const error = searchParams.get('error');

  if (error) {
    // Redirect to dashboard with error
    return NextResponse.redirect(new URL('/dashboard?google_error=' + error, request.url));
  }

  if (!code || !state) {
    return NextResponse.redirect(new URL('/dashboard?google_error=missing_params', request.url));
  }

  // Redirect to a page that will handle the token exchange
  const callbackUrl = new URL('/google-callback', request.url);
  callbackUrl.searchParams.set('code', code);
  callbackUrl.searchParams.set('state', state);

  return NextResponse.redirect(callbackUrl);
}
