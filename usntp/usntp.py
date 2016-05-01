#sntp v4 - https://tools.ietf.org/html/rfc4330
#ntp v3 - https://tools.ietf.org/html/rfc1305
#
#seconds since epoc @ 0h 1/1/1900
#uint64 as
#  uint32 seconds
#  uint32 fraction of seconds (0 padded)
#                           1                   2                   3
#       0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#      |                           Seconds                             |
#      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#      |                  Seconds Fraction (0-padded)                  |
#      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
#if (convention since 1968)
# seconds bit 0 is set(1) range = 1968-2036
# seconds bit 0 not set(0) range = 2036-2104 from 6:28:16 UTC 7/2/2036
#
#NTP UDP on port 123
#
#packet format
#
#                           1                   2                   3
#       0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9  0  1
#      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#      |LI | VN  |Mode |    Stratum    |     Poll      |   Precision    |
#      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#      |                          Root  Delay                           |
#      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#      |                       Root  Dispersion                         |
#      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#      |                     Reference Identifier                       |
#      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#      |                    Reference Timestamp (64)                    |
#      |                                                                |
#      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#      |                    Originate Timestamp (64)                    |
#      |                                                                |
#      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#      |                     Receive Timestamp (64)                     |
#      |                                                                |
#      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#      |                     Transmit Timestamp (64)                    |
#      |                                                                |
#      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#      |                 Key Identifier (optional) (32)                 |
#      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#      |                 Message Digest (optional) (128)                |
#      |                                                                |
#      |                                                                |
#      |                                                                |
#      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# LI = Leap indicator
#   uint2 bit code warning of impending lead-second to be inserted/deleted
#   in last min of current day
#      LI       Meaning
#      ---------------------------------------------
#      0        no warning
#      1        last minute has 61 seconds
#      2        last minute has 59 seconds
#      3        alarm condition (clock not synchronized)
#
# VN = Version Number
#   uint3 code indicating ntp version
#
# Mode
#   uint3 client uni/multicast mode set to 3 in the request, server sets to 4
#      Mode     Meaning
#      ------------------------------------
#      0        reserved
#      1        symmetric active
#      2        symmetric passive
#      3        client
#      4        server
#      5        broadcast
#      6        reserved for NTP control message
#      7        reserved for private use
#
# Stratum
#   uint8 only significant for server msgs
#      Stratum  Meaning
#      ----------------------------------------------
#      0        kiss-o'-death message (see below)
#      1        primary reference (e.g., synchronized by radio clock)
#      2-15     secondary reference (synchronized by NTP or SNTP)
#      16-255   reserved
#
# Poll = Poll Interval
#   uint8, exponent of 2, only used in svr msgs
#
# Precision
#   int8 (signed) svr precision msg = -6 v impresice, -20 v.precise
#
# Root Delay
#   fp32 (signed) fraction pt between bits 15 & 16
#   total roundtrip seconds with
#   only significant svr msgs
#
# Root Dispersion
#   ufp32 fraction pt between bits 15 & 16
#   max tolerence error
#   only significant svr msgs
#
# Reference Identifier
#   32bit string, left just, 0 padded
#   only significant svr msgs
#   for stratum-0 kiss o'death or 1 (primary svr)
#      Code       External Reference Source
#      ------------------------------------------------------------------
#      LOCL       uncalibrated local clock
#      CESM       calibrated Cesium clock
#      RBDM       calibrated Rubidium clock
#      PPS        calibrated quartz clock or other pulse-per-second
#                 source
#      IRIG       Inter-Range Instrumentation Group
#      ACTS       NIST telephone modem service
#      USNO       USNO telephone modem service
#      PTB        PTB (Germany) telephone modem service
#      TDF        Allouis (France) Radio 164 kHz
#      DCF        Mainflingen (Germany) Radio 77.5 kHz
#      MSF        Rugby (UK) Radio 60 kHz
#      WWV        Ft. Collins (US) Radio 2.5, 5, 10, 15, 20 MHz
#      WWVB       Boulder (US) Radio 60 kHz
#      WWVH       Kauai Hawaii (US) Radio 2.5, 5, 10, 15 MHz
#      CHU        Ottawa (Canada) Radio 3330, 7335, 14670 kHz
#      LORC       LORAN-C radionavigation system
#      OMEG       OMEGA radionavigation 
#   for ip4 secondary servers =
#       uint32 ip4 addr of sync source
#   for ip6 and OSI secondary svrs =
#       first 32bits of md5 hash of addr
#
# Reference Timestamp
#   time system clock last set or corrected in 64fp timestamp format
#
# Originate Timestamp
#   time request departed client,64fp timestamp frmt
#
# Receive Timestamp
#   time request arrived at svr or response arrived at client, 64fp timestamp frmt
#
# Transmit Timestamp
#   time response departed server, or request departed svr, 64fp timestamp frmt
#
# Authenitcator (optional)
#   Key Identified and Msg Digest are optional for NTP authenticated svr's
#
