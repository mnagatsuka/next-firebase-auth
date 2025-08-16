export default function DebugPage() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Debug Page</h1>
      <p>If you can see this page, the basic Next.js setup is working.</p>
      <p>MSW should be enabled: {process.env.NEXT_PUBLIC_API_MOCKING}</p>
      <p>API Base URL: {process.env.NEXT_PUBLIC_API_BASE_URL}</p>
    </div>
  )
}