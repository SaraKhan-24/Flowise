import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class UserDashboard extends StatefulWidget {
  const UserDashboard({super.key});

  @override
  State<UserDashboard> createState() => _UserDashboardState();
}

class _UserDashboardState extends State<UserDashboard> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBody: true, // Content flows behind the nav bar
      resizeToAvoidBottomInset: false,
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF2E7D8E), // Deep Teal
              Color(0xFF004D40), // Darker Teal
            ],
          ),
        ),
        child: Stack(
          children: [

            // Content with ScrollView to prevent overflow
            SafeArea(
              bottom: false,
              child: SingleChildScrollView(
                physics: const BouncingScrollPhysics(),
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: Column(
                  children: [
                    const SizedBox(height: 20),
                    if (_currentIndex == 0) _buildHomeScreen(),
                    if (_currentIndex == 1) _buildUsageScreen(),
                    if (_currentIndex == 2) _buildSettingsScreen(),
                    const SizedBox(height: 120), // Essential padding so Nav Bar doesn't cover content
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: _buildGlassBottomNav(),
    );
  }

  // --- SCREEN 1: HOME ---
  Widget _buildHomeScreen() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text("Hi, XYZ!", style: GoogleFonts.poppins(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white)),
        Text("Block A, House 12", style: GoogleFonts.poppins(color: Colors.white70)),
        const SizedBox(height: 30),
        _buildGlassCard(
          child: Column(
            children: [
              Text("Daily Consumption", style: GoogleFonts.poppins(fontWeight: FontWeight.w600, color: Colors.white)),
              const SizedBox(height: 30),
              _buildCircularProgress(),
              const SizedBox(height: 25),
              Text("Goal: 250L", style: GoogleFonts.poppins(color: Colors.white60)),
            ],
          ),
        ),
        const SizedBox(height: 20),
        _buildAlertBox(),
      ],
    );
  }

  // --- SCREEN 2: USAGE ---
  Widget _buildUsageScreen() {
    return Column(
      children: [
        Text("Detailed Usage", style: GoogleFonts.poppins(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white)),
        const SizedBox(height: 30),
        _buildGlassCard(
          child: Column(
            children: [
              const Text("Weekly Consumption", style: TextStyle(color: Colors.white70)),
              const SizedBox(height: 180, child: Center(child: Icon(Icons.bar_chart, size: 120, color: Colors.white))),
              const Divider(color: Colors.white24),
              Text("Total: 1,250L", style: GoogleFonts.poppins(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 18)),
            ],
          ),
        ),
      ],
    );
  }

  // --- SCREEN 3: SETTINGS ---
  Widget _buildSettingsScreen() {
    return Column(
      children: [
        const CircleAvatar(radius: 50, backgroundColor: Colors.white24, child: Icon(Icons.person, size: 50, color: Colors.white)),
        const SizedBox(height: 15),
        Text("XYZ", style: GoogleFonts.poppins(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white)),
        const SizedBox(height: 30),
        _buildGlassTile(Icons.edit, "Edit Profile"),
        _buildGlassTile(Icons.lock_outline, "Change Password"),
        _buildGlassTile(Icons.notifications_none, "Notifications"),
        _buildGlassTile(Icons.logout, "Log Out", isCritical: true),
      ],
    );
  }

  // --- UI HELPERS ---

  Widget _buildGlassCard({required Widget child}) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(30),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 15, sigmaY: 15),
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.all(25),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.1),
            borderRadius: BorderRadius.circular(30),
            border: Border.all(color: Colors.white.withOpacity(0.2), width: 1.5),
          ),
          child: child,
        ),
      ),
    );
  }

  Widget _buildCircularProgress() {
    return Stack(
      alignment: Alignment.center,
      children: [
        SizedBox(
          height: 180, width: 180,
          child: CircularProgressIndicator(
            value: 0.72,
            strokeWidth: 14,
            color: Colors.cyanAccent,
            backgroundColor: Colors.white10,
          ),
        ),
        Column(
          children: [
            Text("180", style: GoogleFonts.poppins(fontSize: 40, fontWeight: FontWeight.bold, color: Colors.white)),
            Text("LITERS", style: GoogleFonts.poppins(fontSize: 12, color: Colors.white70, letterSpacing: 2)),
          ],
        )
      ],
    );
  }

  Widget _buildGlassTile(IconData icon, String title, {bool isCritical = false}) {
    return Container(
      margin: const EdgeInsets.only(bottom: 15),
      child: _buildGlassCard(
        child: Row(
          children: [
            Icon(icon, color: isCritical ? Colors.redAccent : Colors.cyanAccent),
            const SizedBox(width: 20),
            Text(title, style: TextStyle(color: isCritical ? Colors.redAccent : Colors.white, fontSize: 16)),
            const Spacer(),
            const Icon(Icons.chevron_right, color: Colors.white24),
          ],
        ),
      ),
    );
  }

  Widget _buildGlassBottomNav() {
    return Container(
      margin: const EdgeInsets.fromLTRB(25, 0, 25, 30),
      height: 85, // Increased height to fit icons + labels
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(30),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(30),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 15, sigmaY: 15),
          child: BottomNavigationBar(
            currentIndex: _currentIndex,
            onTap: (index) => setState(() => _currentIndex = index),
            backgroundColor: Colors.white.withOpacity(0.1),
            elevation: 0,
            selectedItemColor: Colors.cyanAccent,
            unselectedItemColor: Colors.white38,
            type: BottomNavigationBarType.fixed, // Keeps labels visible
            selectedLabelStyle: GoogleFonts.poppins(fontSize: 12, fontWeight: FontWeight.w600),
            unselectedLabelStyle: GoogleFonts.poppins(fontSize: 12),
            items: const [
              BottomNavigationBarItem(icon: Icon(Icons.home_filled), label: "Home"),
              BottomNavigationBarItem(icon: Icon(Icons.bar_chart_rounded), label: "Usage"),
              BottomNavigationBarItem(icon: Icon(Icons.person), label: "Settings"),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAlertBox() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.redAccent.withOpacity(0.8),
        borderRadius: BorderRadius.circular(50),
      ),
      child: const Row(
        children: [
          Icon(Icons.warning_amber_rounded, color: Colors.white, size: 30),
          SizedBox(width: 15),
          Text("LEAK DETECTED!", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildGlassOrb(double size, Color color) {
    return Container(width: size, height: size, decoration: BoxDecoration(shape: BoxShape.circle, color: color));
  }
}