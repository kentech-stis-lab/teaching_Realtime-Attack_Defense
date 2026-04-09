import React from 'react';

/**
 * Packet capture filter suggestions for each attack type.
 * Shown above the terminal when an attack is running or just completed.
 *
 * Key architecture:
 *   Dashboard (172.20.0.2) → Backend (172.20.1.100:8000) → Juice Shop (172.20.1.10:3000)
 *                                                        → SSH (172.20.0.11:2222)
 *                                                        → FTP (172.20.0.12:21)
 *                                                        → internal-api (172.20.1.30:5000)
 *
 * The filters target the ACTUAL attack traffic (backend→target),
 * NOT the API trigger (dashboard→backend).
 *
 * -d flags: decode non-standard ports as HTTP
 * -V flag: verbose output showing HTTP body with attack payload
 */

const DECODE = '-d tcp.port==3000,http -d tcp.port==5000,http -d tcp.port==8000,http';

const FILTERS = {
  sqli_login_bypass: {
    tshark: `tshark -i any ${DECODE} -V -Y "ip.dst == 172.20.1.10 && http.request.method == POST && http contains \\"login\\""`,
    wireshark: 'ip.dst == 172.20.1.10 && http.request.method == "POST" && http contains "login"',
    desc: 'SQLi Login Bypass - backend→Juice Shop POST /rest/user/login',
    tip: 'payload: {"email": "\' OR 1=1--"}',
    payload: true,
  },
  sqli_union_select: {
    tshark: `tshark -i any ${DECODE} -V -Y "ip.dst == 172.20.1.10 && (http contains \\"UNION\\" || http contains \\"SELECT\\")"`,
    wireshark: 'ip.dst == 172.20.1.10 && (http contains "UNION" || http contains "SELECT")',
    desc: 'SQLi UNION SELECT - backend→Juice Shop with UNION/SELECT',
    tip: 'payload: UNION SELECT in URI query',
    payload: true,
  },
  xss_dom: {
    tshark: `tshark -i any ${DECODE} -V -Y "ip.dst == 172.20.1.10 && (http contains \\"<iframe\\" || http contains \\"<script\\")"`,
    wireshark: 'ip.dst == 172.20.1.10 && (http contains "<iframe" || http contains "<script")',
    desc: 'DOM XSS - backend→Juice Shop iframe/script injection',
    tip: 'payload: <iframe src="javascript:alert()"',
    payload: true,
  },
  xss_reflected: {
    tshark: `tshark -i any ${DECODE} -V -Y "ip.dst == 172.20.1.10 && (http contains \\"<script\\" || http contains \\"onerror\\")"`,
    wireshark: 'ip.dst == 172.20.1.10 && (http contains "<script" || http contains "onerror")',
    desc: 'Reflected XSS - backend→Juice Shop script/onerror injection',
    tip: 'payload: <script>alert()</script> in response',
    payload: true,
  },
  xss_stored: {
    tshark: `tshark -i any ${DECODE} -V -Y "ip.dst == 172.20.1.10 && http.request.method == POST && http contains \\"<script\\""`,
    wireshark: 'ip.dst == 172.20.1.10 && http.request.method == "POST" && http contains "<script"',
    desc: 'Stored XSS - backend→Juice Shop POST with script payload',
    tip: 'payload: <script>alert()</script> in POST body',
    payload: true,
  },
  brute_web: {
    tshark: `tshark -i any ${DECODE} -V -Y "ip.dst == 172.20.1.10 && http.request.method == POST && http.request.uri contains \\"/rest/user/login\\""`,
    wireshark: 'ip.dst == 172.20.1.10 && http.request.method == "POST" && http.request.uri contains "/rest/user/login"',
    desc: 'Web Brute Force - backend→Juice Shop repeated login attempts',
    tip: 'payload: repeated {"email":"...","password":"..."} attempts',
    payload: true,
  },
  brute_ssh: {
    tshark: 'tshark -i any -V -Y "ip.dst == 172.20.0.11 && tcp.dstport == 2222 && ssh"',
    wireshark: 'ip.dst == 172.20.0.11 && tcp.dstport == 2222 && ssh',
    desc: 'SSH Brute Force - backend��SSH server (172.20.0.11:2222)',
    tip: 'repeated SSH handshake + auth failure + reconnect cycles',
    payload: false,
  },
  brute_ftp: {
    tshark: 'tshark -i any -V -Y "tcp.dstport == 21 && (ftp.request.command == USER || ftp.request.command == PASS)"',
    wireshark: 'tcp.dstport == 21 && (ftp.request.command == "USER" || ftp.request.command == "PASS")',
    desc: 'FTP Brute Force - backend→FTP server (172.20.0.12:21)',
    tip: 'payload: USER admin / PASS <wordlist>',
    payload: false,
  },
  bot_scraper: {
    tshark: `tshark -i any ${DECODE} -V -Y "ip.dst == 172.20.1.10 && http.request.method == GET && http.request.uri contains \\"/api/Products\\""`,
    wireshark: 'ip.dst == 172.20.1.10 && http.request.method == "GET" && http.request.uri contains "/api/Products"',
    desc: 'Bot Scraper - backend→Juice Shop rapid GET requests',
    tip: 'payload: GET /api/Products repeated at high rate',
    payload: true,
  },
  dos_slowloris: {
    tshark: `tshark -i any ${DECODE} -V -Y "ip.dst == 172.20.1.10 && tcp.dstport == 3000 && tcp contains \\"Slowloris\\""`,
    wireshark: 'ip.dst == 172.20.1.10 && tcp.dstport == 3000 && tcp contains "Slowloris"',
    desc: 'DoS Slowloris - partial HTTP headers keeping connections alive',
    tip: 'payload: User-Agent "Slowloris PoC" + X-Slowloris-* keep-alive headers',
    payload: true,
  },
  portscan: {
    tshark: 'tshark -i any -V -Y "ip.src == 172.20.0.100 && ip.dst != 172.20.0.100 && tcp.flags.syn == 1 && tcp.flags.ack == 0"',
    wireshark: 'ip.src == 172.20.0.100 && ip.dst != 172.20.0.100 && tcp.flags.syn == 1 && tcp.flags.ack == 0',
    desc: 'Port Scan - SYN to many hosts/ports on 172.20.0.0/24',
    tip: 'SYN packets to 254 hosts x 12 ports (frontend-net scan)',
    payload: false,
  },
  infiltration: {
    tshark: `tshark -i any ${DECODE} -V -Y "ip.dst == 172.20.1.30 || ip.dst == 172.20.1.20"`,
    wireshark: 'ip.dst == 172.20.1.30 || ip.dst == 172.20.1.20',
    desc: 'Infiltration - backend→internal-api (5000) / MySQL (3306)',
    tip: 'payload: internal API access + DB queries',
    payload: true,
  },
};

export default function PacketFilter({ activeAttackId }) {
  const filter = activeAttackId ? FILTERS[activeAttackId] : null;

  if (!filter) {
    return (
      <div className="packet-filter-bar empty">
        <span className="packet-filter-icon">&#x1F50D;</span>
        <span className="packet-filter-label">Packet Filter</span>
        <span className="packet-filter-hint">Run an attack to see the capture filter</span>
      </div>
    );
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).catch(() => {});
  };

  return (
    <div className="packet-filter-bar active">
      <div className="packet-filter-top">
        <span className="packet-filter-icon">&#x1F50D;</span>
        <span className="packet-filter-label">Packet Filter</span>
        <span className="packet-filter-desc">{filter.desc}</span>
      </div>
      <div className="packet-filter-filters">
        <div className="packet-filter-item">
          <span className="packet-filter-tool">Wireshark</span>
          <code className="packet-filter-code">{filter.wireshark}</code>
          <button
            className="btn btn-sm"
            onClick={() => copyToClipboard(filter.wireshark)}
            title="Copy filter"
          >
            Copy
          </button>
        </div>
        <div className="packet-filter-item">
          <span className="packet-filter-tool">tshark</span>
          <code className="packet-filter-code">{filter.tshark}</code>
          <button
            className="btn btn-sm"
            onClick={() => copyToClipboard(filter.tshark)}
            title="Copy command"
          >
            Copy
          </button>
        </div>
      </div>
      <div className="packet-filter-decode-note">
        <span className="packet-filter-tip-payload">{filter.tip}</span>
        <br />
        {filter.payload ? (
          <>
            <strong>tshark</strong>: -V 플래그로 HTTP body(공격 payload) 표시
            &nbsp;|&nbsp;
            <strong>Wireshark</strong>: 패킷 우클릭 &rarr; Follow &rarr; HTTP Stream
          </>
        ) : (
          <>
            <strong>tshark</strong>: -V ���래그로 패킷 상세 표시
            &nbsp;|&nbsp;
            <strong>Wireshark</strong>: 패킷 우클릭 &rarr; Follow &rarr; TCP Stream
          </>
        )}
        {filter.payload && (
          <>
            <br />
            <strong>Decode As</strong>: Wireshark GUI &rarr; Analyze &rarr; Decode As &rarr; TCP port 3000/5000 = HTTP
          </>
        )}
      </div>
    </div>
  );
}
