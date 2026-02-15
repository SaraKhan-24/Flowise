import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AdminDashboard extends StatefulWidget {
  const AdminDashboard({super.key});

  @override
  State<AdminDashboard> createState() => _AdminDashboardState();
}

class _AdminDashboardState extends State<AdminDashboard> {
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBody: true, // Allows the bottom nav to be transparent over the background
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF2E7D8E), Color(0xFF1A4D57)], // Deep Teal Gradient
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildHeader(),
                const SizedBox(height: 25),
                _buildQuickStats(),
                const SizedBox(height: 20),
                _buildGlassMapCard(),
                const SizedBox(height: 20),
                _buildCriticalAlerts(),
                const SizedBox(height: 100), // Space for Bottom Nav
              ],
            ),
          ),
        ),
      ),
      bottomNavigationBar: _buildLiquidBottomNav(),
    );
  }

  // --- UI COMPONENTS ---

  Widget _buildHeader() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("System Overview",
                style: GoogleFonts.poppins(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white)),
            Text("Monitor real-time water flow",
                style: GoogleFonts.poppins(fontSize: 14, color: Colors.white70)),
          ],
        ),
        const CircleAvatar(
          backgroundColor: Colors.white24,
          child: Icon(Icons.notifications_none, color: Colors.white),
        )
      ],
    );
  }

  Widget _buildQuickStats() {
    return Row(
      children: [
        Expanded(
          child: _buildStatCard("Active Leaks", "3", Colors.redAccent.withOpacity(0.8), Icons.warning_amber_rounded),
        ),
        const SizedBox(width: 15),
        Expanded(
          child: _buildStatCard("System Health", "Operational", Colors.greenAccent.withOpacity(0.4), Icons.check_circle_outline),
        ),
      ],
    );
  }

  Widget _buildStatCard(String title, String value, Color color, IconData icon) {
    return _glassMorphicWrapper(
      child: Container(
        padding: const EdgeInsets.all(15),
        decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(20)),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: Colors.white, size: 30),
            const SizedBox(height: 10),
            Text(title, style: GoogleFonts.poppins(color: Colors.white, fontSize: 12)),
            Text(value, style: GoogleFonts.poppins(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }

  Widget _buildGlassMapCard() {
    return _glassMorphicWrapper(
      child: Container(
        padding: const EdgeInsets.all(15),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("Real-Time Sensor Map",
                style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.w600)),
            const SizedBox(height: 15),
            Container(
              height: 150,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(15),
                image: const DecorationImage(
                  image: NetworkImage('https://images.squarespace-cdn.com/content/v1/54ffbb4ce4b060d47343e74b/1454000302798-967E9G6G5G6G5G6G5G6G/image-asset.jpeg'),
                  fit: BoxFit.cover,
                ),
              ),
              child: const Center(child: Icon(Icons.location_on, color: Colors.redAccent, size: 40)),
            ),
            const SizedBox(height: 10),
            Text("Sector G-8, Valve 12 active", style: GoogleFonts.poppins(color: Colors.white70, fontSize: 12)),
          ],
        ),
      ),
    );
  }

  Widget _buildCriticalAlerts() {
    return _glassMorphicWrapper(
      child: Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildTrendItem("Pressure", Icons.trending_up, Colors.cyanAccent),
                _buildTrendItem("Flow Rate", Icons.trending_up, Colors.tealAccent),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTrendItem(String label, IconData icon, Color color) {
    return Column(
      children: [
        Text(label, style: GoogleFonts.poppins(color: Colors.white, fontSize: 12)),
        Icon(icon, color: color, size: 40),
        Text("Normal", style: GoogleFonts.poppins(color: color, fontSize: 10)),
      ],
    );
  }

  // --- FILTERS / NAVIGATION ---

  Widget _buildLiquidBottomNav() {
    return Container(
      margin: const EdgeInsets.all(20),
      height: 70,
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.15),
        borderRadius: BorderRadius.circular(30),
        border: Border.all(color: Colors.white.withOpacity(0.2)),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(30),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _navIcon(0, Icons.home_filled, "Home"),
              _navIcon(1, Icons.fiber_new, "New"),
              _navIcon(2, Icons.check_circle, "Resolved"),
              _navIcon(3, Icons.filter_list, "Filter"),
            ],
          ),
        ),
      ),
    );
  }

  Widget _navIcon(int index, IconData icon, String label) {
    bool isSelected = _selectedIndex == index;
    return GestureDetector(
      onTap: () => setState(() => _selectedIndex = index),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: isSelected ? Colors.cyanAccent : Colors.white60, size: 28),
          Text(label, style: TextStyle(color: isSelected ? Colors.cyanAccent : Colors.white60, fontSize: 10)),
        ],
      ),
    );
  }

  // --- UTILS ---

  Widget _glassMorphicWrapper({required Widget child}) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(20),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.1),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: Colors.white.withOpacity(0.4)),
          ),
          child: child,
        ),
      ),
    );
  }
}