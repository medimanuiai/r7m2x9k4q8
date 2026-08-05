import "../styles/globals.css";

export const metadata = {
  title: "Birth to Career | Jyothishyam",
  description:
    "An account-free, ephemeral Lahiri-sidereal Birth to Career reading.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <header className="site-header">
          <a className="brand" href="/" aria-label="Jyothishyam home">
            <span className="brand-mark" aria-hidden="true">
              J
            </span>
            <span>
              <strong>Jyothishyam</strong>
              <small>Birth → Career</small>
            </span>
          </a>
          <span className="privacy-chip">Account-free · Ephemeral</span>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
