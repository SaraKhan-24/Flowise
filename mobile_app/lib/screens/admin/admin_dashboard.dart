import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_database/firebase_database.dart';

class AdminDashboard extends StatefulWidget {
  const AdminDashboard({super.key});

  @override
  State<AdminDashboard> createState() => _AdminDashboardState();
}

class _AdminDashboardState extends State<AdminDashboard> {
  late final DatabaseReference _dbRef;

  @override
  void initState() {
    super.initState();
    // Using instanceFor to ensure we hit the exact DB URL
    _dbRef = FirebaseDatabase.instanceFor(
      app: Firebase.app(),
      databaseURL: 'https://flowwise-90f95-default-rtdb.firebaseio.com',
    ).ref();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      body: StreamBuilder(
        stream: _dbRef.onValue,
        builder: (context, snapshot) {
          if (snapshot.hasError) {
            return _buildStatusUI("Firebase Error: ${snapshot.error}", isError: true);
          }

          if (snapshot.hasData && snapshot.data!.snapshot.value != null) {
            final rawData = snapshot.data!.snapshot.value;
            Map<dynamic, dynamic> sensorData = {};

            // SMART DATA DETECTION:
            // 1. Check if data is inside a 'sensors' key
            if (rawData is Map && rawData.containsKey('sensors')) {
              sensorData = Map<dynamic, dynamic>.from(rawData['sensors'] as Map);
            } 
            // 2. Check if data is just sitting at the root directly
            else if (rawData is Map && rawData.containsKey('F1')) {
              sensorData = Map<dynamic, dynamic>.from(rawData);
            }

            if (sensorData.isNotEmpty) {
              return _buildDashboardUI(sensorData);
            } else {
              return _buildStatusUI("Database connected, but no 'F1', 'F2', 'P1', or 'P2' keys found.\n\nPlease check your data structure.");
            }
          }

          return _buildStatusUI("Connecting to Real-Time Database...\n(Check your Rules if this takes too long)");
        },
      ),
    );
  }

  Widget _buildDashboardUI(Map data) {
    // tryParse ensures the app doesn't crash if sensors send weird strings
    double f1 = double.tryParse(data['F1']?.toString() ?? '0') ?? 0.0;
    double f2 = double.tryParse(data['F2']?.toString() ?? '0') ?? 0.0;
    double p1 = double.tryParse(data['P1']?.toString() ?? '0') ?? 0.0;
    double p2 = double.tryParse(data['P2']?.toString() ?? '0') ?? 0.0;
    int binaryLeak = int.tryParse(data['Leak']?.toString() ?? '0') ?? 0;

    int activeLeakZone = 0;
    String alertMsg = "System Secure";

    if (binaryLeak == 1) {
      if (f1 > f2 + 1.5) {
        activeLeakZone = 3;
        alertMsg = "Leak detected between F1 and F2";
      } else if (p1 > p2 + 5.0) {
        activeLeakZone = 4;
        alertMsg = "Leak detected between F2 and P2";
      } else {
        activeLeakZone = 2;
        alertMsg = "Leak detected between P1 and F1";
      }
    }

    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeader(),
            const SizedBox(height: 25),
            Row(
              children: [
                Expanded(child: _buildComparisonCard("Flow (L/min)", f1, f2, Colors.tealAccent, activeLeakZone == 3)),
                const SizedBox(width: 15),
                Expanded(child: _buildComparisonCard("Pressure (PSI)", p1, p2, Colors.orangeAccent, activeLeakZone == 4)),
              ],
            ),
            const SizedBox(height: 25),
            _buildBlueprintCard(activeLeakZone, alertMsg),
            const SizedBox(height: 25),
            Text("Pressure Analytics", style: GoogleFonts.poppins(color: Colors.white70, fontSize: 14)),
            const SizedBox(height: 10),
            _buildAnalyticsChart(p1, p2),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusUI(String message, {bool isError = false}) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(30.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (!isError) const CircularProgressIndicator(color: Colors.cyanAccent),
            if (isError) const Icon(Icons.error_outline, color: Colors.red, size: 50),
            const SizedBox(height: 20),
            Text(message, textAlign: TextAlign.center, style: GoogleFonts.poppins(color: isError ? Colors.redAccent : Colors.white54, fontSize: 13)),
          ],
        ),
      ),
    );
  }

  // --- UI COMPONENTS ---

  Widget _buildHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text("FloWise Admin", style: GoogleFonts.poppins(fontSize: 26, fontWeight: FontWeight.bold, color: Colors.white)),
        Text("Real-Time Differential Analysis", style: GoogleFonts.poppins(fontSize: 14, color: Colors.white54)),
      ],
    );
  }

  Widget _buildComparisonCard(String title, double s1, double s2, Color color, bool isAlert) {
    return Container(
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: isAlert ? Colors.redAccent : Colors.white10),
      ),
      child: Column(
        children: [
          Text(title, style: const TextStyle(color: Colors.white70, fontSize: 11)),
          const SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _val("S1", s1, color),
              const Icon(Icons.compare_arrows, color: Colors.white24, size: 14),
              _val("S2", s2, isAlert ? Colors.redAccent : color),
            ],
          ),
        ],
      ),
    );
  }

  Widget _val(String label, double val, Color color) {
    return Column(
      children: [
        Text(label, style: const TextStyle(color: Colors.white38, fontSize: 9)),
        Text(val.toStringAsFixed(1), style: GoogleFonts.poppins(color: color, fontSize: 16, fontWeight: FontWeight.bold)),
      ],
    );
  }

  Widget _buildBlueprintCard(int leakZone, String msg) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(color: const Color(0xFF1E293B), borderRadius: BorderRadius.circular(20)),
      child: Column(
        children: [
          SizedBox(
            height: 150,
            width: double.infinity,
            child: CustomPaint(painter: LinearPipelinePainter(activeLeakZone: leakZone)),
          ),
          const SizedBox(height: 15),
          Text(msg, style: GoogleFonts.poppins(color: leakZone > 0 ? Colors.redAccent : Colors.tealAccent, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildAnalyticsChart(double p1, double p2) {
    return Container(
      height: 180,
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(color: const Color(0xFF1E293B), borderRadius: BorderRadius.circular(20)),
      child: LineChart(
        LineChartData(
          gridData: const FlGridData(show: false),
          titlesData: const FlTitlesData(show: false),
          borderData: FlBorderData(show: false),
          lineBarsData: [
            LineChartBarData(
              spots: [FlSpot(0, p1), FlSpot(1, p2)],
              isCurved: true,
              color: Colors.cyanAccent,
              barWidth: 4,
              belowBarData: BarAreaData(show: true, color: Colors.cyanAccent.withValues(alpha: 0.1)),
              dotData: const FlDotData(show: true),
            ),
          ],
        ),
      ),
    );
  }
}

class LinearPipelinePainter extends CustomPainter {
  final int activeLeakZone;
  LinearPipelinePainter({required this.activeLeakZone});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..style = PaintingStyle.stroke..strokeWidth = 6.0..strokeCap = StrokeCap.round;
    double w = size.width; double h = size.height; double y = h / 2;
    final nodes = [Offset(20, y), Offset(w * 0.25, y), Offset(w * 0.50, y), Offset(w * 0.75, y), Offset(w - 20, y)];

    for (int i = 0; i < nodes.length - 1; i++) {
      paint.color = (activeLeakZone == i + 1) ? Colors.redAccent : Colors.cyanAccent.withValues(alpha: 0.3);
      canvas.drawLine(nodes[i], nodes[i + 1], paint);
    }
    _drawNode(canvas, nodes[0], "PUMP", Colors.white);
    _drawNode(canvas, nodes[1], "P1", Colors.orangeAccent);
    _drawNode(canvas, nodes[2], "F1", Colors.tealAccent);
    _drawNode(canvas, nodes[3], "F2", Colors.tealAccent);
    _drawNode(canvas, nodes[4], "P2", Colors.orangeAccent);
  }

  void _drawNode(Canvas canvas, Offset pos, String name, Color color) {
    canvas.drawCircle(pos, 6, Paint()..color = color);
    final tp = TextPainter(text: TextSpan(text: name, style: GoogleFonts.poppins(color: color, fontSize: 10, fontWeight: FontWeight.bold)), textDirection: TextDirection.ltr)..layout();
    tp.paint(canvas, Offset(pos.dx - (tp.width / 2), pos.dy - 25));
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
