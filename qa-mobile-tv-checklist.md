# Mobile, Android TV and Smart TV QA Checklist

**Purpose:** reusable test-design checklist for mobile and television applications.  
**Coverage focus:** Android · iOS · Android TV · Smart TV · remote-control interaction · media playback.

> This document is a reusable QA checklist, not a claim that every listed scenario has been executed on every device model. The actual execution record must include device, OS/firmware, app build, result and evidence.

## 1. Test matrix to record per project

| Dimension | Values to record |
|---|---|
| Application | App name, package/bundle ID, build number, release channel |
| Device | Manufacturer, exact model, hardware revision if relevant |
| Platform | Android / iOS / Android TV / Smart TV platform |
| Software | OS version, firmware version, security patch where relevant |
| Display | Resolution, density, orientation, overscan where relevant |
| Network | Wi-Fi / Ethernet / mobile data, proxy/VPN, bandwidth conditions |
| Account | Role, entitlement, locale, test-data identifier |
| Execution | Date, tester, test suite version, result, evidence link |

Never report "tested on Android" as a complete compatibility statement. Report the actual device and OS matrix.

## 2. Installation, launch and upgrade

| ID | Scenario | Expected result | Priority |
|---|---|---|---|
| MOB-001 | Fresh install from the agreed distribution channel | Install completes; app launches without crash | P1 |
| MOB-002 | Upgrade from the previous supported build | User state and supported settings are preserved | P1 |
| MOB-003 | First launch after install | Correct onboarding, permissions and initial state | P1 |
| MOB-004 | Launch after force stop / device restart | App returns to a valid state | P1 |
| MOB-005 | Insufficient storage during install/update | Clear error; no corrupted partial installation | P2 |
| MOB-006 | Clear app data / reinstall | Defined first-run behavior; no stale local state | P2 |

For Android devices, where debugging is enabled and permitted, common checks include package installation/update, application launch and log capture using Android SDK Platform Tools (ADB). Installation commands and device access depend on the test environment and build distribution method.

## 3. Android and iOS lifecycle

| ID | Scenario | Expected result | Priority |
|---|---|---|---|
| APP-001 | Send app to background and resume | No unexpected reset, duplicate action or data loss | P1 |
| APP-002 | Receive a call, notification or system interruption | App recovers without corrupting the current flow | P1 |
| APP-003 | Lock and unlock device during an active flow | Session and UI state follow requirements | P1 |
| APP-004 | Rotate device where supported | Layout remains usable; entered data is preserved | P2 |
| APP-005 | Switch between apps and return | No stale screen or duplicated request | P1 |
| APP-006 | Session expires while app is backgrounded | User is re-authenticated safely; protected data is not exposed | P1 |
| APP-007 | Permission granted, denied and later changed in settings | App handles each state without crash | P2 |
| APP-008 | App receives a deep link / push notification | Correct destination, authorization and fallback behavior | P2 |

## 4. Network and resilience

| ID | Scenario | Expected result | Priority |
|---|---|---|---|
| NET-001 | Switch Wi-Fi to mobile data during a request | Request completes once or fails clearly; no duplicate business action | P1 |
| NET-002 | Lose connectivity before submit | User sees actionable feedback; no false success | P1 |
| NET-003 | Restore connectivity after offline state | App recovers and refreshes the correct state | P1 |
| NET-004 | Slow response / timeout | Loading state is clear; retry policy is safe | P1 |
| NET-005 | Server returns 4xx / 5xx | Error is handled without leaking internal details | P1 |
| NET-006 | Repeat submit after delayed response | No duplicate payment/order/action where idempotency is required | P1 |

## 5. Android TV and Smart TV interaction

| ID | Scenario | Expected result | Priority |
|---|---|---|---|
| TV-001 | Launch app from TV home screen | Correct initial screen; no focus loss | P1 |
| TV-002 | Navigate all primary controls with D-pad | Focus is visible and follows a predictable order | P1 |
| TV-003 | Open and close a dialog / overlay | Focus moves into the dialog and returns to a valid element | P1 |
| TV-004 | Press Back from nested screens | Navigation returns to the expected previous state | P1 |
| TV-005 | Hold or rapidly repeat a remote key | No accidental repeated purchase/action or UI lockup | P1 |
| TV-006 | Select a card while focus is near viewport edge | Focus scrolls into view; selected item remains visible | P2 |
| TV-007 | Navigate after loading or content refresh | Focus remains valid or is deliberately reset | P1 |
| TV-008 | Disconnect / reconnect remote where applicable | App remains usable after input resumes | P2 |
| TV-009 | Exit and relaunch during playback | Playback and session state follow requirements | P1 |

## 6. Media playback scenarios

| ID | Scenario | Expected result | Priority |
|---|---|---|---|
| MED-001 | Start playback from a content card | Correct content starts; metadata matches selection | P1 |
| MED-002 | Pause and resume | Playback state and control indicators stay in sync | P1 |
| MED-003 | Seek forward / backward | Timeline and actual playback position remain consistent | P1 |
| MED-004 | Network interruption during playback | Buffering/retry/error state is understandable; recovery works | P1 |
| MED-005 | Switch audio track or subtitles | Selected track is applied and remains selected as specified | P2 |
| MED-006 | Change resolution / adaptive bitrate | Playback remains stable or degrades gracefully | P2 |
| MED-007 | Content unavailable / expired / geo-restricted | Correct entitlement or availability message is shown | P1 |
| MED-008 | Return from player to catalogue | Focus and scroll position are restored as specified | P2 |

## 7. Visual, accessibility and compatibility checks

- Text is readable at TV viewing distance and is not clipped by safe-area/overscan behavior.
- Focus is distinguishable from hover, selected and disabled states.
- Focus order does not trap the user or skip essential actions.
- Touch controls on mobile have usable hit areas and do not overlap.
- Dynamic text size, system font settings and supported localization do not break layouts.
- Loading, empty, error and offline states are visually distinct.
- Orientation, resolution and aspect ratio changes are handled where supported.

## 8. Build installation and diagnostics

Record the supported installation path for each target:
- Android / Android TV: approved APK or internal distribution channel; ADB only when device settings and policy permit it.
- iOS: signed build through the agreed TestFlight, MDM or internal distribution process.
- OEM Smart TV platforms: vendor-specific development mode, package format, signing and installation tooling.

For every defect, capture:
- Exact model and OS/firmware.
- App build and installation source.
- Steps, expected and actual result.
- Frequency and workaround.
- Timestamp and relevant app/system logs.
- Network conditions and account state.
- Screenshot or screen recording where safe and permitted.

Do not include real credentials, personal data or payment details in evidence.

## 9. Suggested execution report

| Field | Example value |
|---|---|
| Build | 1.4.0-rc.3 |
| Device / OS | Exact model and OS/firmware |
| Test suite | TV smoke / playback regression |
| Executed | 18 / 20 |
| Passed / Failed / Blocked | 16 / 1 / 1 |
| Defects | Links and severity |
| Residual risk | Device variants not covered |
| Recommendation | Go / Conditional go / No-go |

The numbers above are an example report format, not an actual test run.

---

**Related:** [QA Engineering Strategy](./qa-engineering-strategy.md) · [QA Portfolio](./qa-portfolio.md)
